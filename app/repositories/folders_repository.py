import logging

from sqlalchemy import delete, func, select, update

from core.exceptions import FolderNotFoundException
from models.models import Folders
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class FoldersRepository(BaseRepository):
    async def get_by_id(self, user_id: int, folder_id: int) -> Folders:
        query = select(Folders).where(
            Folders.id == folder_id,
            Folders.user_id == user_id,
        )
        result = await self.session.execute(query)
        folder = result.scalar_one_or_none()

        if folder is None:
            raise FolderNotFoundException(folder_id)

        return folder

    async def find_by_path(self, user_id: int, full_path: str) -> Folders | None:
        query = select(Folders).where(
            Folders.user_id == user_id,
            Folders.full_path == full_path,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_children(
            self,
            user_id: int,
            parent_id: int | None,
    ) -> list[Folders]:
        query = (
            select(Folders)
            .where(
                Folders.user_id == user_id,
                Folders.parent_id.is_(None)
                if parent_id is None
                else Folders.parent_id == parent_id,
            )
            .order_by(func.lower(Folders.name))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_paths(self, user_id: int, paths: list[str]) -> list[Folders]:
        if not paths:
            return []

        query = select(Folders).where(
            Folders.user_id == user_id,
            Folders.full_path.in_(paths),
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(
            self,
            user_id: int,
            name: str,
            full_path: str,
            parent_id: int | None,
    ) -> Folders:
        folder = Folders(
            user_id=user_id,
            name=name,
            full_path=full_path,
            parent_id=parent_id,
        )
        self.session.add(folder)
        await self.session.flush()
        await self.session.refresh(folder)
        logger.info(
            "Создана папка id=%s путь=%s (user_id=%s)",
            folder.id, folder.full_path, user_id,
        )
        return folder

    async def rename(
            self,
            user_id: int,
            folder: Folders,
            new_name: str,
            new_full_path: str,
            old_prefix: str,
            new_prefix: str,
    ) -> Folders:
        """Обновляет папку и пути всех вложенных папок.

        Объекты в MinIO перемещает сервис — репозиторий отвечает только за БД.
        """
        tail = func.substr(Folders.full_path, len(old_prefix) + 1)
        descendants_query = (
            update(Folders)
            .where(
                Folders.user_id == user_id,
                Folders.id != folder.id,
                Folders.full_path.startswith(old_prefix, autoescape=True),
            )
            .values(full_path=new_prefix + tail)
        )
        await self.session.execute(descendants_query)

        folder.name = new_name
        folder.full_path = new_full_path

        await self.session.flush()
        await self.session.refresh(folder)
        logger.info(
            "Переименована папка id=%s: %s -> %s",
            folder.id, old_prefix, new_prefix,
        )
        return folder

    async def delete_subtree(self, user_id: int, folder_id: int) -> None:
        """Удаляет папку; вложенные папки и файлы уходят по ON DELETE CASCADE."""
        query = delete(Folders).where(
            Folders.id == folder_id,
            Folders.user_id == user_id,
        )
        await self.session.execute(query)
        await self.session.flush()
        logger.info("Удалена папка id=%s (user_id=%s)", folder_id, user_id)

    async def count(self, user_id: int) -> int:
        query = select(func.count(Folders.id)).where(Folders.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()
