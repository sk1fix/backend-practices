# Currency API 💱
REST API для управления валютами и конвертации курсов с использованием FastAPI, PostgreSQL и SQLAlchemy

## 📋 Описание проекта
Currency API — это асинхронный веб-сервис для работы с валютами и обменными курсами. Проект демонстрирует практические навыки backend-разработки с применением современных технологий и паттернов проектирования.

## Основные возможности
 - 💰 Управление валютами (CRUD операции)

 - 📊 Работа с обменными курсами

 - 🔄 Конвертация валют

 - 🗄️ Асинхронная работа с PostgreSQL через SQLAlchemy

 - 🐳 Полная контейнеризация с Docker

 - 📝 Миграции базы данных через Alembic

## 🛠️ Технологический стек
 - Framework: FastAPI

 - База данных: PostgreSQL

 - ORM: SQLAlchemy

 - Миграции: Alembic

 - Валидация: Pydantic

 - ASGI сервер: Uvicorn

 - Контейнеризация: Docker & Docker Compose
## 🚀 Быстрый старт
### Предварительные требования
 - Docker и Docker Compose
 - Python 3.11+ (для локальной разработки)

### Установка и запуск
 - Клонируйте репозиторий

```bash
git clone https://github.com/sk1fix/backend-practices.git
cd backend-practices
git checkout sql
```
 - Настройте переменные окружения

```bash
cp example.env .env
# Отредактируйте .env при необходимости
```
 - Запустите приложение с помощью Docker Compose

```bash
docker-compose up --build
```
Приложение будет доступно по адресу: http://localhost:5050

## API документация
После запуска приложения, автоматически сгенерированная документация доступна по следующим адресам:

Swagger UI: http://localhost:5050/docs

ReDoc: http://localhost:5050/redoc

## 📡 API Endpoints
### Currencies (Валюты)
 - GET /currencies - Получить список всех валют
 - GET /currencies/{currency_code} - Получить валюту по ID
 - POST /currencies - Создать новую валюту
 - PUT /currencies/{currency_id} - Обновить валюту
 - DELETE /currencies/{currency_id} - Удалить валюту

### Exchange Rates (Обменные курсы)
 - GET /exchange-rates - Получить список курсов
 - GET /exchange-rates/{exchange_rate_code} - Получить курс по кодам валют
 - POST /exchange-rates - Создать новый курс
 - PUT /exchange-rates/{exchange_rate_code} - Обновить курс
 - DELETE /exchange-rates/{exchange_rate_id} - Удалить курс

### Conversion (Конвертация)
 - POST /convert - Конвертировать сумму из одной валюты в другую

## Паттерны проектирования
 - Repository Pattern - Абстракция работы с данными
 - Service Layer - Бизнес-логика отделена от контроллеров
 - Dependency Injection - Управление зависимостями через FastAPI
 - Data Mapper - Преобразование между моделями БД и DTO