from pydantic import BaseModel


class UsersRegisterDto(BaseModel):
    login: str
    hashed_password: str
    username: str


class UsersLoginDto(BaseModel):
    login: str
    password: str


class UserHashPass(BaseModel):
    hashed_password: str


class UserInfoDto(BaseModel):
    username: str
    used_storage_bytes: int
    storage_quota_bytes: int


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"