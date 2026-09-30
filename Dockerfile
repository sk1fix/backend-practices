# --- Этап 1: сборка SPA ---
FROM node:24-alpine AS web-build

# Базовый путь сборки: '/' или '/cloud-storage/' (должен совпадать с ROOT_PATH)
ARG VITE_BASE_PATH=/

WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build


# --- Этап 2: backend + собранная статика ---
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LOGS_PATH=/app/logs \
    SPA_DIR=/app/static

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/
COPY --from=web-build /web/dist /app/static

EXPOSE 8000

CMD ["sh", "/app/entrypoint.sh"]
