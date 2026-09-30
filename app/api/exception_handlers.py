import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
            request: Request,
            exc: StarletteHTTPException,
    ) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error(
                "%s %s -> %s: %s (request_id=%s)",
                request.method, request.url.path, exc.status_code, exc.detail,
                _request_id(request),
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": _request_id(request),
            },
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request,
            exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "Ошибка валидации %s %s: %s (request_id=%s)",
            request.method, request.url.path, exc.errors(),
            _request_id(request),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": jsonable_encoder(exc.errors()),
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
            request: Request,
            exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Необработанная ошибка %s %s (request_id=%s)",
            request.method, request.url.path, _request_id(request),
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Внутренняя ошибка сервера",
                "request_id": _request_id(request),
            },
        )
