import logging

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from core.config import settings
from core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException
)
from models.models import Users
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class AuthRepository(BaseRepository):
    async def create_user(
            self,
            login: str,
            hashed_password: str,
            username: str,
            quota_bytes: int = settings.DEFAULT_QUOTA_BYTES,
    ) -> Users:
        if await self._find_by_login(login) is not None:
            raise UserAlreadyExistsException("логином", login)

        user = Users(
            login=login,
            hashed_password=hashed_password,
            username=username,
            storage_quota_bytes=quota_bytes,
        )
        self.session.add(user)

        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise UserAlreadyExistsException("логином", login)

        await self.session.refresh(user)
        logger.info(
            "Зарегистрирован пользователь id=%s login=%s", user.id, user.login)
        return user

    async def find_by_login(self, login: str) -> Users | None:
        return await self._find_by_login(login)

    async def get_by_id(self, user_id: int) -> Users:
        query = select(Users).where(Users.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundException(str(user_id))

        return user

    async def reserve_storage(self, user_id: int, delta: int) -> bool:
        """Атомарно резервирует место в квоте.

        Проверка и изменение выполняются одним UPDATE, поэтому параллельные
        загрузки не могут превысить квоту. False — места не хватает.
        """
        if delta <= 0:
            await self.add_used_storage(user_id, delta)
            return True

        query = (
            update(Users)
            .where(
                Users.id == user_id,
                Users.used_storage + delta <= Users.storage_quota_bytes,
            )
            .values(used_storage=Users.used_storage + delta)
            .returning(Users.used_storage)
        )
        result = await self.session.execute(query)
        return result.first() is not None

    async def get_storage_state(self, user_id: int) -> tuple[int, int]:
        """Свежие (занято, квота) прямо из БД, минуя identity map сессии."""
        query = select(Users.used_storage, Users.storage_quota_bytes).where(
            Users.id == user_id)
        result = await self.session.execute(query)
        used_storage, quota = result.one()
        return int(used_storage), int(quota)

    async def add_used_storage(self, user_id: int, delta: int) -> None:
        """Атомарно изменяет занятое место (delta может быть отрицательной)."""
        if delta == 0:
            return

        query = (
            update(Users)
            .where(Users.id == user_id)
            .values(used_storage=Users.used_storage + delta)
        )
        await self.session.execute(query)

    async def _find_by_login(self, login: str) -> Users | None:
        query = select(Users).where(Users.login == login)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
