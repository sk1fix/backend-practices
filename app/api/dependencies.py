from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from services.auth import AuthService
from repositories.auth_repository import AuthRepository
from core.security import get_user_data_from_token
from core.exceptions import InvalidTokenException


async def get_token_from_cookie(request: Request) -> str:
    return request.cookies.get("access_token")


async def get_current_user(
        token: str = Depends(get_token_from_cookie)
) -> dict:
    if not token:
        raise InvalidTokenException("Токен отсутствует. Войдите в систему.")

    user_data = get_user_data_from_token(token)

    return user_data


async def get_auth_repository(
        session: AsyncSession = Depends(get_db)
) -> AuthRepository:
    return AuthRepository(session)


async def get_auth_service(
        repo: AsyncSession = Depends(get_auth_repository)
) -> AuthService:
    return AuthService(repo)
