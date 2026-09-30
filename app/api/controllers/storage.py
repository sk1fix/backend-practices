from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from api.dependencies import get_current_user, get_storage_service
from models.models import Users
from schemas.storage import UsageDto
from services.storage import StorageService

storage = APIRouter(tags=["Storage"])


@storage.get("/storage/usage", summary="Занятое место и квота")
async def get_usage(
        user: Users = Depends(get_current_user),
        service: StorageService = Depends(get_storage_service),
) -> UsageDto:
    return await service.get_usage(user)


@storage.get("/health", summary="Проверка БД и хранилища")
async def health(
        service: StorageService = Depends(get_storage_service),
) -> JSONResponse:
    health_status = await service.get_health()

    return JSONResponse(
        status_code=200 if health_status.status == "ok" else 503,
        content=health_status.model_dump(),
    )
