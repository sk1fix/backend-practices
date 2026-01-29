from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from services.auth import AuthService
from repositories.auth_repository import AuthRepository


async def get_auth_repository(
        session: AsyncSession = Depends(get_db)
) -> AuthRepository:
    return AuthRepository(session)

async def get_auth_service(
        repo: AsyncSession = Depends(get_auth_repository)
) -> AuthService:
    return AuthService(repo)
