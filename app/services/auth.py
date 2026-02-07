from fastapi import HTTPException

from core.security import verify_password, get_password_hash, get_user_data_from_token, create_token
from schemas.auth import UserRegisterDto, Token, UserResponseDto, UserLoginDto
from core.exceptions import InvalidCredentialsException


class AuthService:
    def __init__(self, repo):
        self.repo = repo

    async def register_user(self, data: UserRegisterDto) -> UserResponseDto:
        hashed_password = get_password_hash(data.hashed_password)
        new_dto = UserRegisterDto(
            login=data.login,
            hashed_password=hashed_password,
            username=data.username
        )
        result = await self.repo.create_user(new_dto)
        response_dto = UserResponseDto(
            login=result.login,
            username=result.username
        )
        return response_dto

    async def login_user(self, data: UserLoginDto) -> Token:
        _ = await self.repo.get_by_login(data.login)
        hash_pass = await self.repo.get_pass_by_login(data.login)
        if verify_password(data.password, hash_pass.hashed_password):
            token_payload = {
                "sub": hash_pass.login,
                "username": hash_pass.username,
                "user_id": hash_pass.id
            }
            access_token = create_token(token_payload)
            return Token(access_token=access_token)
        else:
            raise InvalidCredentialsException()
