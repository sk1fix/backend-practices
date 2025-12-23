from pydantic import PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env"),
        case_sensitive=False
    )

    HOST: str
    PORT: int

    LOGS_PATH: str

    DB_URL: PostgresDsn


settings = Settings()
settings.DB_URL = str(settings.DB_URL)
