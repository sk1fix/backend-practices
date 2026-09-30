import asyncio
import logging

from sqlalchemy.exc import IntegrityError

from core.exceptions import FolderAlreadyExistsException
from core.object_storage import ObjectStorage
from core.paths import (
    cumulative_paths,
    folder_prefix,
    join_path,
    parent_path_of,
    path_name,
    validate_name
)
from models.models import Folders, Users
from repositories.auth_repository import AuthRepository
from repositories.files_repository import FilesRepository
from repositories.folders_repository import FoldersRepository
from schemas.storage import (
    ROOT_BREADCRUMB_NAME,
    BreadcrumbDto,
    FileResponseDto,
    FolderCreateDto,
    FolderListingDto,
    FolderResponseDto
)

logger = logging.getLogger(__name__)


class FoldersService:
    def __init__(
            self,
            folders_repo: FoldersRepository,
            files_repo: FilesRepository,
            auth_repo: AuthRepository,
            storage: ObjectStorage,
    ):
        self.folders_repo = folders_repo
        self.files_repo = files_repo
        self.auth_repo = auth_repo
        self.storage = storage

    async def list_contents(
            self,
            user: Users,
            parent_id: int | None,
    ) -> FolderListingDto:
        folder = await self._resolve_folder(user.id, parent_id)
        folder_path = folder.full_path if folder else ""

        children = await self.folders_repo.list_children(user.id, parent_id)
        files = await self.files_repo.list_by_folder(user.id, parent_id)
        breadcrumbs = await self._build_breadcrumbs(user.id, folder_path)

        return FolderListingDto(
            breadcrumbs=breadcrumbs,
            folders=[
                FolderResponseDto.model_validate(child)
                for child in children
            ],
            files=[
                FileResponseDto.model_validate(file)
                for file in files
            ],
        )

    async def create_folder(
            self,
            user: Users,
            data: FolderCreateDto,
    ) -> FolderResponseDto:
        name = validate_name(data.name)
        parent = await self._resolve_folder(user.id, data.parent_id)
        parent_path = parent.full_path if parent else ""
        full_path = join_path(parent_path, name)

        if await self.folders_repo.find_by_path(user.id, full_path) is not None:
            raise FolderAlreadyExistsException(name)

        try:
            folder = await self.folders_repo.create(
                user_id=user.id,
                name=name,
                full_path=full_path,
                parent_id=parent.id if parent else None,
            )
            await self.folders_repo.commit()
        except IntegrityError:
            await self.folders_repo.rollback()
            raise FolderAlreadyExistsException(name)

        return FolderResponseDto.model_validate(folder)

    async def rename_folder(
            self,
            user: Users,
            folder_id: int,
            new_name: str,
    ) -> FolderResponseDto:
        name = validate_name(new_name)
        folder = await self.folders_repo.get_by_id(user.id, folder_id)
        new_full_path = join_path(parent_path_of(folder.full_path), name)

        if new_full_path == folder.full_path:
            return FolderResponseDto.model_validate(folder)

        if await self.folders_repo.find_by_path(user.id, new_full_path) is not None:
            raise FolderAlreadyExistsException(name)

        old_prefix = folder_prefix(folder.full_path)
        new_prefix = folder_prefix(new_full_path)
        bucket = self.storage.bucket_name(user.id)

        moved = await asyncio.to_thread(
            self.storage.move_prefix, bucket, old_prefix, new_prefix)

        try:
            folder = await self.folders_repo.rename(
                user_id=user.id,
                folder=folder,
                new_name=name,
                new_full_path=new_full_path,
                old_prefix=old_prefix,
                new_prefix=new_prefix,
            )
            await self.files_repo.rename_storage_keys(
                user.id, old_prefix, new_prefix)
            await self.folders_repo.commit()
        except Exception:
            await self.folders_repo.rollback()
            await self._rollback_move(bucket, new_prefix, old_prefix, moved)
            raise

        return FolderResponseDto.model_validate(folder)

    async def delete_folder(self, user: Users, folder_id: int) -> None:
        folder = await self.folders_repo.get_by_id(user.id, folder_id)
        prefix = folder_prefix(folder.full_path)

        total_size, _ = await self.files_repo.aggregate_by_prefix(
            user.id, prefix)

        await self.folders_repo.delete_subtree(user.id, folder_id)
        await self.auth_repo.add_used_storage(user.id, -total_size)
        await self.folders_repo.commit()

        bucket = self.storage.bucket_name(user.id)
        try:
            await asyncio.to_thread(self.storage.remove_prefix, bucket, prefix)
        except Exception:  # noqa: BLE001 - записи уже удалены, это мусор в S3
            logger.exception(
                "Не удалось удалить объекты по префиксу %s/%s — "
                "они остались в хранилище",
                bucket, prefix,
            )

    async def _resolve_folder(
            self,
            user_id: int,
            folder_id: int | None,
    ) -> Folders | None:
        if folder_id is None:
            return None

        return await self.folders_repo.get_by_id(user_id, folder_id)

    async def _build_breadcrumbs(
            self,
            user_id: int,
            folder_path: str,
    ) -> list[BreadcrumbDto]:
        breadcrumbs = [BreadcrumbDto(id=None, name=ROOT_BREADCRUMB_NAME)]

        if not folder_path:
            return breadcrumbs

        paths = cumulative_paths(folder_path)
        folders = {
            folder.full_path: folder
            for folder in await self.folders_repo.list_by_paths(user_id, paths)
        }

        for path in paths:
            folder = folders.get(path)
            breadcrumbs.append(BreadcrumbDto(
                id=folder.id if folder else None,
                name=folder.name if folder else path_name(path),
            ))

        return breadcrumbs

    async def _rollback_move(
            self,
            bucket: str,
            new_prefix: str,
            old_prefix: str,
            moved: int,
    ) -> None:
        if not moved:
            return

        logger.error(
            "Откат перемещения объектов: %s -> %s", new_prefix, old_prefix)

        try:
            await asyncio.to_thread(
                self.storage.move_prefix, bucket, new_prefix, old_prefix)
        except Exception:  # noqa: BLE001
            logger.exception(
                "Не удалось откатить перемещение объектов %s -> %s",
                new_prefix, old_prefix,
            )
