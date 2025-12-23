from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = APP_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        case_sensitive=False
    )

    HOST: str
    PORT: int

    LOGS_PATH: str

    DB_URL: PostgresDsn


def get_settings() -> Settings:
    s = Settings()
    s.DB_URL = str(s.DB_URL)
    return s


settings = get_settings()
