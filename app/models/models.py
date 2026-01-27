from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    username: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
