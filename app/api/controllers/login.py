from fastapi import Depends, APIRouter

from dependencies import get_auth_service
from services.auth import AuthService

auth = APIRouter(tags=["Auth route"])

@auth.post('/auth/register', summary="Register route", tags=["Auth route"])
async def register(data: str, service: AuthService = Depends(get_auth_service)) -> str:
    result = await service.register_user(data)
    return result