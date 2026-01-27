from pydantic import BaseModel


class UserRegisterDto(BaseModel):
    login: str
    passsword: str
    username: str

class UserLoginDto(BaseModel):
    login: str
    password: str