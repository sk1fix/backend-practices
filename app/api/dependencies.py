from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from services.auth import AuthService
from app.repositories.auth_repository import AuthRepository


async def get_auth_repository(
        session: AsyncSession = Depends(get_db)
) -> AuthRepository:
    return AuthRepository(session)

async def get_auth_service(
        db: AsyncSession = Depends(get_db)
) -> AuthService:
    repo = AuthRepository(db)
    return AuthService(repo)
