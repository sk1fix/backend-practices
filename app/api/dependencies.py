from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import (
    FileTooLargeException,
    InvalidTokenException,
    UserNotFoundException
)
from core.object_storage import ObjectStorage
from core.object_storage import get_object_storage as build_object_storage
from core.security import decode_token
from database.session import get_db
from models.models import Users
from repositories.auth_repository import AuthRepository
from repositories.files_repository import FilesRepository
from repositories.folders_repository import FoldersRepository
from services.auth import AuthService
from services.files import FilesService
from services.folders import FoldersService
from services.storage import StorageService

ACCESS_TOKEN_COOKIE = "access_token"
MULTIPART_OVERHEAD_BYTES = 1024 * 1024


@lru_cache
def get_object_storage() -> ObjectStorage:
    """Клиент MinIO — потокобезопасный синглтон на процесс."""
    return build_object_storage()


async def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get(ACCESS_TOKEN_COOKIE)


async def get_auth_repository(
        session: AsyncSession = Depends(get_db),
) -> AuthRepository:
    return AuthRepository(session)


async def get_folders_repository(
        session: AsyncSession = Depends(get_db),
) -> FoldersRepository:
    return FoldersRepository(session)


async def get_files_repository(
        session: AsyncSession = Depends(get_db),
) -> FilesRepository:
    return FilesRepository(session)


async def get_current_user(
        token: str | None = Depends(get_token_from_cookie),
        repo: AuthRepository = Depends(get_auth_repository),
) -> Users:
    if not token:
        raise InvalidTokenException("Токен отсутствует. Войдите в систему.")

    payload = decode_token(token)
    user_id = payload.get("user_id")

    if not isinstance(user_id, int):
        raise InvalidTokenException()

    try:
        return await repo.get_by_id(user_id)
    except UserNotFoundException:
        raise InvalidTokenException("Пользователь не найден. Войдите в систему.")


async def get_auth_service(
        repo: AuthRepository = Depends(get_auth_repository),
        storage: ObjectStorage = Depends(get_object_storage),
) -> AuthService:
    return AuthService(repo, storage)


async def get_folders_service(
        folders_repo: FoldersRepository = Depends(get_folders_repository),
        files_repo: FilesRepository = Depends(get_files_repository),
        auth_repo: AuthRepository = Depends(get_auth_repository),
        storage: ObjectStorage = Depends(get_object_storage),
) -> FoldersService:
    return FoldersService(folders_repo, files_repo, auth_repo, storage)


async def get_files_service(
        files_repo: FilesRepository = Depends(get_files_repository),
        folders_repo: FoldersRepository = Depends(get_folders_repository),
        auth_repo: AuthRepository = Depends(get_auth_repository),
        storage: ObjectStorage = Depends(get_object_storage),
) -> FilesService:
    return FilesService(files_repo, folders_repo, auth_repo, storage)


async def get_storage_service(
        session: AsyncSession = Depends(get_db),
        auth_repo: AuthRepository = Depends(get_auth_repository),
        files_repo: FilesRepository = Depends(get_files_repository),
        folders_repo: FoldersRepository = Depends(get_folders_repository),
        storage: ObjectStorage = Depends(get_object_storage),
) -> StorageService:
    return StorageService(session, auth_repo, files_repo, folders_repo, storage)


async def enforce_content_length(request: Request) -> None:
    """Отклоняет слишком большие тела до разбора multipart."""
    content_length = request.headers.get("content-length")

    if content_length is None:
        return

    try:
        length = int(content_length)
    except ValueError:
        return

    if length > settings.MAX_UPLOAD_SIZE_BYTES + MULTIPART_OVERHEAD_BYTES:
        raise FileTooLargeException(settings.MAX_UPLOAD_SIZE_BYTES)
