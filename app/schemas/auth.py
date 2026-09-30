from pydantic import BaseModel, ConfigDict, Field

LOGIN_PATTERN = r"^[A-Za-z0-9_.-]{3,64}$"


class UserRegisterDto(BaseModel):
    login: str = Field(
        min_length=3,
        max_length=64,
        pattern=LOGIN_PATTERN,
        description="Логин: латиница, цифры, «_», «-», «.»",
    )
    password: str = Field(min_length=8, max_length=128)
    username: str = Field(min_length=1, max_length=64)


class UserLoginDto(BaseModel):
    login: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    username: str


class UserProfileDto(UserResponseDto):
    used_storage: int
    storage_quota_bytes: int
