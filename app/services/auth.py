from fastapi import HTTPException

from core.security import verify_password, get_password_hash, get_username_from_token, create_token
from schemas.auth import UsersRegisterDto, Token


class AuthService:
    def __init__(self, repo):
        self.repo = repo

    async def register_user(self, data):
        existing = await self.repo.get_by_login(data.login)
        if existing:
            raise HTTPException(400, "User with this login already exists")

        existing_by_username = await self.repo.get_by_username(data.username)
        if existing_by_username:
            raise HTTPException(400, "User with this username already exists")

        hashed_password = get_password_hash(data.hashed_password)
        new_dto = UsersRegisterDto(
            login=data.login,
            hashed_password=hashed_password,
            username=data.username
        )
        result = await self.repo.create_user(new_dto)
        return result

    async def login_user(self, data):
        existing = await self.repo.get_by_login(data.login)
        if not existing:
            raise HTTPException(401, "No user with this login")

        hash_pass = await self.repo.get_pass_by_login(data.login)
        if verify_password(data.password, hash_pass.hashed_password):
            result = Token(access_token=create_token(data.login))
            return result
        else:
            raise HTTPException(401, "Bad password")

    async def get_current_user(self, token):
        username = get_username_from_token(token)
        existing = await self.repo.get_by_username(username)
        if existing:
            return existing
        else:
            raise HTTPException(401, "You need login")
