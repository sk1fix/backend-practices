import logging

from sqlalchemy import func, select, update

from core.exceptions import FileNotFoundException
from models.models import Files, utcnow
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class FilesRepository(BaseRepository):
    async def get_by_id(self, user_id: int, file_id: int) -> Files:
        query = select(Files).where(
            Files.id == file_id,
            Files.user_id == user_id,
        )
        result = await self.session.execute(query)
        file = result.scalar_one_or_none()

        if file is None:
            raise FileNotFoundException(file_id)

        return file

    async def find_by_key(self, user_id: int, storage_key: str) -> Files | None:
        query = select(Files).where(
            Files.user_id == user_id,
            Files.storage_key == storage_key,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_folder(
            self,
            user_id: int,
            folder_id: int | None,
    ) -> list[Files]:
        query = (
            select(Files)
            .where(
                Files.user_id == user_id,
                Files.folder_id.is_(None)
                if folder_id is None
                else Files.folder_id == folder_id,
            )
            .order_by(func.lower(Files.filename))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(
            self,
            user_id: int,
            folder_id: int | None,
            filename: str,
            storage_key: str,
            size: int,
            mime_type: str,
    ) -> Files:
        file = Files(
            user_id=user_id,
            folder_id=folder_id,
            filename=filename,
            storage_key=storage_key,
            size=size,
            mime_type=mime_type,
        )
        self.session.add(file)
        await self.session.flush()
        await self.session.refresh(file)
        logger.info(
            "Создана запись файла id=%s ключ=%s (user_id=%s, %s байт)",
            file.id, storage_key, user_id, size,
        )
        return file

    async def update_content(
            self,
            file: Files,
            size: int,
            mime_type: str,
    ) -> Files:
        file.size = size
        file.mime_type = mime_type
        file.updated_at = utcnow()
        await self.session.flush()
        await self.session.refresh(file)
        logger.info("Перезаписан файл id=%s (%s байт)", file.id, size)
        return file

    async def rename(self, file: Files, filename: str, storage_key: str) -> Files:
        file.filename = filename
        file.storage_key = storage_key
        file.updated_at = utcnow()
        await self.session.flush()
        await self.session.refresh(file)
        logger.info("Переименован файл id=%s -> %s", file.id, filename)
        return file

    async def delete(self, file: Files) -> None:
        await self.session.delete(file)
        await self.session.flush()
        logger.info("Удалена запись файла id=%s", file.id)

    async def rename_storage_keys(
            self,
            user_id: int,
            old_prefix: str,
            new_prefix: str,
    ) -> None:
        """Переписывает ключи файлов при переименовании папки."""
        tail = func.substr(Files.storage_key, len(old_prefix) + 1)
        query = (
            update(Files)
            .where(
                Files.user_id == user_id,
                Files.storage_key.startswith(old_prefix, autoescape=True),
            )
            .values(storage_key=new_prefix + tail, updated_at=utcnow())
        )
        await self.session.execute(query)

    async def aggregate_by_prefix(
            self,
            user_id: int,
            prefix: str,
    ) -> tuple[int, int]:
        """Возвращает (суммарный размер, количество) файлов внутри префикса."""
        query = select(
            func.coalesce(func.sum(Files.size), 0),
            func.count(Files.id),
        ).where(
            Files.user_id == user_id,
            Files.storage_key.startswith(prefix, autoescape=True),
        )
        result = await self.session.execute(query)
        total_size, files_count = result.one()
        return int(total_size), int(files_count)

    async def count(self, user_id: int) -> int:
        query = select(func.count(Files.id)).where(Files.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()
