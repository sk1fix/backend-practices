import logging
import time
import uuid

logger = logging.getLogger("app.request")


class RequestLoggingMiddleware:
    """Чистый ASGI-middleware: не буферизует тело ответа, поэтому безопасен
    для отдачи файлов через StreamingResponse."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex[:12]
        scope.setdefault("state", {})["request_id"] = request_id
        started_at = time.perf_counter()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = message.setdefault("headers", [])
                headers.append((b"x-request-id", request_id.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - started_at) * 1000
            client = scope.get("client")
            message = "%s %s -> %s (%.1f мс) ip=%s request_id=%s"

            if status_code >= 500:
                logger.error(
                    message,
                    scope["method"], scope["path"], status_code, duration_ms,
                    client[0] if client else "-", request_id,
                )
            elif status_code >= 400:
                logger.warning(
                    message,
                    scope["method"], scope["path"], status_code, duration_ms,
                    client[0] if client else "-", request_id,
                )
            else:
                logger.info(
                    message,
                    scope["method"], scope["path"], status_code, duration_ms,
                    client[0] if client else "-", request_id,
                )
