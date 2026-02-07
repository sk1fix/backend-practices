from pydantic import BaseModel


class UserRegisterDto(BaseModel):
    login: str
    hashed_password: str
    username: str


class UserLoginDto(BaseModel):
    login: str
    password: str


class UserResponseDto(BaseModel):
    login: str
    fullname: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
