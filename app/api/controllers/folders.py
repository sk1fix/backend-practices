from fastapi import APIRouter, Depends, Query, status

from api.dependencies import get_current_user, get_folders_service
from models.models import Users
from schemas.storage import (
    FolderCreateDto,
    FolderListingDto,
    FolderRenameDto,
    FolderResponseDto
)
from services.folders import FoldersService

folders = APIRouter(prefix="/folders", tags=["Folders"])


@folders.get("", summary="Содержимое папки (папки и файлы)")
async def list_contents(
        parent_id: int | None = Query(
            default=None,
            description="ID папки; не указан — корень",
        ),
        user: Users = Depends(get_current_user),
        service: FoldersService = Depends(get_folders_service),
) -> FolderListingDto:
    return await service.list_contents(user, parent_id)


@folders.post(
    "",
    summary="Создать папку",
    status_code=status.HTTP_201_CREATED,
)
async def create_folder(
        data: FolderCreateDto,
        user: Users = Depends(get_current_user),
        service: FoldersService = Depends(get_folders_service),
) -> FolderResponseDto:
    return await service.create_folder(user, data)


@folders.patch("/{folder_id}", summary="Переименовать папку")
async def rename_folder(
        folder_id: int,
        data: FolderRenameDto,
        user: Users = Depends(get_current_user),
        service: FoldersService = Depends(get_folders_service),
) -> FolderResponseDto:
    return await service.rename_folder(user, folder_id, data.name)


@folders.delete(
    "/{folder_id}",
    summary="Удалить папку со всем содержимым",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_folder(
        folder_id: int,
        user: Users = Depends(get_current_user),
        service: FoldersService = Depends(get_folders_service),
) -> None:
    await service.delete_folder(user, folder_id)
