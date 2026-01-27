from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(20), primary_key=True)
    password: Mapped[str] = mapped_column(String(30))
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
