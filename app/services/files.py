import asyncio
import logging
import mimetypes
import os
import re
from collections.abc import Iterator

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError

from core.config import settings
from core.exceptions import (
    FileAlreadyExistsException,
    FileTooLargeException,
    StorageQuotaExceededException
)
from core.object_storage import ObjectStorage
from core.paths import build_storage_key, validate_name
from models.models import Files, Users
from repositories.auth_repository import AuthRepository
from repositories.files_repository import FilesRepository
from repositories.folders_repository import FoldersRepository
from schemas.storage import FileResponseDto

logger = logging.getLogger(__name__)

FALLBACK_MIME_TYPE = "application/octet-stream"


class FilesService:
    def __init__(
            self,
            files_repo: FilesRepository,
            folders_repo: FoldersRepository,
            auth_repo: AuthRepository,
            storage: ObjectStorage,
    ):
        self.files_repo = files_repo
        self.folders_repo = folders_repo
        self.auth_repo = auth_repo
        self.storage = storage

    async def upload(
            self,
            user: Users,
            upload: UploadFile,
            folder_id: int | None,
            overwrite: bool,
    ) -> FileResponseDto:
        folder = (
            None
            if folder_id is None
            else await self.folders_repo.get_by_id(user.id, folder_id)
        )
        folder_path = folder.full_path if folder else ""
        filename = validate_name(self._base_name(upload.filename))
        size = self._measure(upload.file)

        if size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileTooLargeException(settings.MAX_UPLOAD_SIZE_BYTES)

        storage_key = build_storage_key(folder_path, filename)
        bucket = self.storage.bucket_name(user.id)

        existing = await self.files_repo.find_by_key(user.id, storage_key)

        if existing is not None and not overwrite:
            raise FileAlreadyExistsException(filename)

        previous_size = existing.size if existing is not None else 0

        reserved = await self.auth_repo.reserve_storage(
            user.id, size - previous_size)

        if not reserved:
            used_storage, quota = await self.auth_repo.get_storage_state(user.id)
            raise StorageQuotaExceededException(
                required=size,
                available=max(quota - used_storage, 0),
            )

        content_type = (
            upload.content_type
            or mimetypes.guess_type(filename)[0]
            or FALLBACK_MIME_TYPE
        )

        upload.file.seek(0)

        try:
            await asyncio.to_thread(self.storage.ensure_bucket, bucket)
            await asyncio.to_thread(
                self.storage.put_object,
                bucket,
                storage_key,
                upload.file,
                size,
                content_type,
            )
        except Exception:
            await self.files_repo.rollback()
            raise

        try:
            if existing is not None:
                file = await self.files_repo.update_content(
                    existing, size, content_type)
            else:
                file = await self.files_repo.create(
                    user_id=user.id,
                    folder_id=folder.id if folder else None,
                    filename=filename,
                    storage_key=storage_key,
                    size=size,
                    mime_type=content_type,
                )

            await self.files_repo.commit()
        except IntegrityError:
            await self.files_repo.rollback()
            raise FileAlreadyExistsException(filename)
        except Exception:
            await self.files_repo.rollback()
            logger.exception(
                "Объект %s/%s загружен, но запись в БД не сохранена",
                bucket, storage_key,
            )
            raise

        return FileResponseDto.model_validate(file)

    async def open_download(
            self,
            user: Users,
            file_id: int,
    ) -> tuple[Files, Iterator[bytes]]:
        file = await self.files_repo.get_by_id(user.id, file_id)
        bucket = self.storage.bucket_name(user.id)

        await asyncio.to_thread(
            self.storage.stat_object, bucket, file.storage_key)

        return file, self.storage.iter_object(bucket, file.storage_key)

    async def rename_file(
            self,
            user: Users,
            file_id: int,
            new_filename: str,
    ) -> FileResponseDto:
        filename = validate_name(new_filename)
        file = await self.files_repo.get_by_id(user.id, file_id)
        old_key = file.storage_key
        new_key = build_storage_key(self._parent_path_of_key(file), filename)

        if new_key == old_key:
            return FileResponseDto.model_validate(file)

        if await self.files_repo.find_by_key(user.id, new_key) is not None:
            raise FileAlreadyExistsException(filename)

        bucket = self.storage.bucket_name(user.id)
        await asyncio.to_thread(
            self.storage.copy_object, bucket, old_key, new_key)

        try:
            file = await self.files_repo.rename(file, filename, new_key)
            await self.files_repo.commit()
        except Exception:
            await self.files_repo.rollback()
            await self._rollback_copy(bucket, new_key, old_key)
            raise

        try:
            await asyncio.to_thread(self.storage.remove_object, bucket, old_key)
        except Exception:  # noqa: BLE001 - файл уже переименован в БД
            logger.exception(
                "Не удалось удалить старый объект %s/%s",
                bucket, old_key,
            )

        return FileResponseDto.model_validate(file)

    async def delete_file(self, user: Users, file_id: int) -> None:
        file = await self.files_repo.get_by_id(user.id, file_id)
        bucket = self.storage.bucket_name(user.id)
        storage_key = file.storage_key
        size = file.size

        await self.files_repo.delete(file)
        await self.auth_repo.add_used_storage(user.id, -size)
        await self.files_repo.commit()

        try:
            await asyncio.to_thread(
                self.storage.remove_object, bucket, storage_key)
        except Exception:  # noqa: BLE001 - запись уже удалена
            logger.exception(
                "Не удалось удалить объект %s/%s — он остался в хранилище",
                bucket, storage_key,
            )

    @staticmethod
    def _base_name(filename: str | None) -> str:
        """Отбрасывает путь из имени файла (учитывает оба разделителя)."""
        return re.split(r"[\\/]", filename or "")[-1]

    @staticmethod
    def _measure(stream) -> int:
        """Размер загруженного файла (multipart уже разобран в temp-файл)."""
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0)
        return size

    @staticmethod
    def _parent_path_of_key(file: Files) -> str:
        if file.storage_key.endswith(file.filename):
            return file.storage_key[:-len(file.filename)].rstrip("/")

        return ""

    async def _rollback_copy(
            self,
            bucket: str,
            new_key: str,
            old_key: str,
    ) -> None:
        try:
            await asyncio.to_thread(
                self.storage.copy_object, bucket, new_key, old_key)
            await asyncio.to_thread(self.storage.remove_object, bucket, new_key)
        except Exception:  # noqa: BLE001
            logger.exception(
                "Не удалось откатить переименование объекта %s -> %s",
                old_key, new_key,
            )
