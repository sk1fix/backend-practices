from fastapi import Depends, APIRouter

from api.dependencies import get_auth_service
from services.auth import AuthService
from schemas.auth import UsersRegisterDto, UsersLoginDto, Token

auth = APIRouter(tags=["Auth route"])

@auth.post('/auth/register', summary="Register route", tags=["Auth route"])
async def register(data: UsersRegisterDto, service: AuthService = Depends(get_auth_service)) -> UsersRegisterDto:
    result = await service.register_user(data)
    return result


@auth.post('/auth/login', summary="Login route", tags=["Auth route"])
async def login(data: UsersLoginDto, service: AuthService = Depends(get_auth_service)) -> Token:
    result = await service.login_user(data)
    return result