from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, pool_pre_ping=True)
session = async_sessionmaker(engine, expire_on_commit=False)
