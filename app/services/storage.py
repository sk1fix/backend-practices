import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.object_storage import ObjectStorage
from models.models import Users
from repositories.auth_repository import AuthRepository
from repositories.files_repository import FilesRepository
from repositories.folders_repository import FoldersRepository
from schemas.storage import HealthDto, UsageDto

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(
            self,
            session: AsyncSession,
            auth_repo: AuthRepository,
            files_repo: FilesRepository,
            folders_repo: FoldersRepository,
            storage: ObjectStorage,
    ):
        self.session = session
        self.auth_repo = auth_repo
        self.files_repo = files_repo
        self.folders_repo = folders_repo
        self.storage = storage

    async def get_usage(self, user: Users) -> UsageDto:
        used_storage, quota = await self.auth_repo.get_storage_state(user.id)

        return UsageDto(
            used_storage=used_storage,
            storage_quota_bytes=quota,
            files_count=await self.files_repo.count(user.id),
            folders_count=await self.folders_repo.count(user.id),
        )

    async def get_health(self) -> HealthDto:
        database = "ok"
        storage = "ok"

        try:
            await self.session.execute(text("SELECT 1"))
        except Exception as error:  # noqa: BLE001 - health-check не должен падать
            logger.error("Проверка БД не прошла: %s", error)
            database = "error"

        if not await asyncio.to_thread(self.storage.health):
            storage = "error"

        return HealthDto(
            status="ok" if database == "ok" and storage == "ok" else "degraded",
            database=database,
            storage=storage,
        )
