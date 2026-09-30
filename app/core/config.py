from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
APP_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = APP_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOGS_PATH: str = "logs"
    LOG_LEVEL: str = "INFO"
    SPA_DIR: str = "web/dist"
    CORS_ORIGINS: str = ""
    # Внешний префикс пути, под которым приложение отдаётся прокси
    # (nginx снимает его перед передачей в контейнер). '/' или пусто — корень.
    ROOT_PATH: str = ""

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    DB_URL: str | None = None

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_HOURS: int = 48
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: bool = False
    MINIO_REGION: str = "us-east-1"

    DEFAULT_QUOTA_BYTES: int = 2 * 1024 ** 3
    MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 ** 3

    @property
    def database_url(self) -> str:
        if self.DB_URL:
            return self.DB_URL

        return (
            "postgresql+asyncpg://"
            f"{quote_plus(self.POSTGRES_USER)}:{quote_plus(self.POSTGRES_PASSWORD)}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def spa_path(self) -> Path:
        path = Path(self.SPA_DIR)
        return path if path.is_absolute() else PROJECT_DIR / path

    @property
    def root_path(self) -> str:
        """Нормализованный префикс: '/cloud-storage' или '' для корня."""
        stripped = self.ROOT_PATH.strip("/")
        return f"/{stripped}" if stripped else ""

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def access_token_expire_seconds(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_HOURS * 60 * 60


settings = Settings()
