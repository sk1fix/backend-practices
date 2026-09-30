from datetime import datetime

from pydantic import BaseModel, ConfigDict

ROOT_BREADCRUMB_NAME = "Мои файлы"


class FolderCreateDto(BaseModel):
    name: str
    parent_id: int | None = None


class FolderRenameDto(BaseModel):
    name: str


class FileRenameDto(BaseModel):
    filename: str


class FolderResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    create_date: datetime
    updated_at: datetime


class FileResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    folder_id: int | None
    size: int
    mime_type: str
    create_date: datetime
    updated_at: datetime


class BreadcrumbDto(BaseModel):
    id: int | None
    name: str


class FolderListingDto(BaseModel):
    breadcrumbs: list[BreadcrumbDto]
    folders: list[FolderResponseDto]
    files: list[FileResponseDto]


class UsageDto(BaseModel):
    used_storage: int
    storage_quota_bytes: int
    files_count: int
    folders_count: int


class HealthDto(BaseModel):
    status: str
    database: str
    storage: str
