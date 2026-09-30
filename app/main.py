import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.controllers.files import files
from api.controllers.folders import folders
from api.controllers.login import auth
from api.controllers.storage import storage
from api.exception_handlers import register_exception_handlers
from api.middleware import RequestLoggingMiddleware
from core.config import settings
from core.logging import setup_logging
from database.base import engine

setup_logging()
logger = logging.getLogger(__name__)

API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Запуск сервиса: БД=%s, MinIO=%s",
        settings.POSTGRES_HOST,
        settings.MINIO_ENDPOINT,
    )
    yield
    await engine.dispose()
    logger.info("Сервис остановлен")


cloud_app = FastAPI(
    title="Cloud Storage",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=None,
    openapi_url=f"{API_PREFIX}/openapi.json",
)

cloud_app.add_middleware(RequestLoggingMiddleware)

if settings.cors_origins:
    cloud_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(cloud_app)

cloud_app.include_router(auth, prefix=API_PREFIX)
cloud_app.include_router(folders, prefix=API_PREFIX)
cloud_app.include_router(files, prefix=API_PREFIX)
cloud_app.include_router(storage, prefix=API_PREFIX)

spa_path = settings.spa_path
spa_index = spa_path / "index.html"

if spa_index.is_file():
    logger.info("Статика SPA отдаётся из %s", spa_path)

    @cloud_app.get("/{path:path}", include_in_schema=False)
    async def spa(path: str) -> FileResponse:
        if path == "api" or path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Не найдено")

        candidate = (spa_path / path).resolve()

        if path and candidate.is_file() and candidate.is_relative_to(spa_path.resolve()):
            return FileResponse(candidate)

        return FileResponse(spa_index)
else:
    logger.warning(
        "Каталог SPA не найден (%s): API будет работать без веб-интерфейса",
        spa_path,
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:cloud_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
