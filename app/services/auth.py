import asyncio
import logging

from core.config import settings
from core.exceptions import InvalidCredentialsException
from core.object_storage import ObjectStorage
from core.security import (
    create_token,
    get_password_hash,
    verify_password
)
from models.models import Users
from repositories.auth_repository import AuthRepository
from schemas.auth import (
    UserLoginDto,
    UserProfileDto,
    UserRegisterDto,
    UserResponseDto
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, repo: AuthRepository, storage: ObjectStorage):
        self.repo = repo
        self.storage = storage

    async def register_user(self, data: UserRegisterDto) -> UserResponseDto:
        user = await self.repo.create_user(
            login=data.login,
            hashed_password=get_password_hash(data.password),
            username=data.username,
            quota_bytes=settings.DEFAULT_QUOTA_BYTES,
        )
        await self.repo.commit()

        bucket = self.storage.bucket_name(user.id)
        try:
            await asyncio.to_thread(self.storage.ensure_bucket, bucket)
        except Exception:  # noqa: BLE001 - бакет создастся при первой загрузке
            logger.exception(
                "Не удалось создать бакет %s — он будет создан при загрузке",
                bucket,
            )

        return UserResponseDto.model_validate(user)

    async def login_user(
            self,
            data: UserLoginDto,
    ) -> tuple[UserResponseDto, str]:
        user = await self.repo.find_by_login(data.login)

        if user is None or not verify_password(data.password, user.hashed_password):
            logger.warning("Неудачная попытка входа: login=%s", data.login)
            raise InvalidCredentialsException()

        token = create_token({
            "sub": user.login,
            "user_id": user.id,
            "username": user.username,
        })
        logger.info("Пользователь вошёл: id=%s login=%s", user.id, user.login)
        return UserResponseDto.model_validate(user), token

    @staticmethod
    def get_profile(user: Users) -> UserProfileDto:
        return UserProfileDto.model_validate(user)
