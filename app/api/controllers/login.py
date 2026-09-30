from fastapi import APIRouter, Depends, Response, status

from api.dependencies import (
    ACCESS_TOKEN_COOKIE,
    get_auth_service,
    get_current_user
)
from core.config import settings
from models.models import Users
from schemas.auth import (
    UserLoginDto,
    UserProfileDto,
    UserRegisterDto,
    UserResponseDto
)
from services.auth import AuthService

auth = APIRouter(prefix="/auth", tags=["Auth route"])


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.access_token_expire_seconds,
        path="/",
    )


@auth.post(
    "/register",
    summary="Регистрация",
    status_code=status.HTTP_201_CREATED,
)
async def register(
        data: UserRegisterDto,
        service: AuthService = Depends(get_auth_service),
) -> UserResponseDto:
    return await service.register_user(data)


@auth.post("/login", summary="Вход")
async def login(
        response: Response,
        data: UserLoginDto,
        service: AuthService = Depends(get_auth_service),
) -> UserResponseDto:
    user, token = await service.login_user(data)
    _set_auth_cookie(response, token)
    return user


@auth.post(
    "/logout",
    summary="Выход",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(response: Response) -> None:
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE, path="/")


@auth.get("/me", summary="Текущий пользователь")
async def me(user: Users = Depends(get_current_user)) -> UserProfileDto:
    return AuthService.get_profile(user)
