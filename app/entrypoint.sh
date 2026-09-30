#!/bin/sh
set -e

echo "[entrypoint] применяю миграции Alembic"
alembic upgrade head

echo "[entrypoint] запускаю uvicorn"
exec uvicorn main:cloud_app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips '*'
