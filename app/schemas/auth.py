from pydantic import BaseModel


class UsersRegisterDto(BaseModel):
    login: str
    hashed_password: str
    username: str

class UsersLoginDto(BaseModel):
    login: str
    hashed_password: str