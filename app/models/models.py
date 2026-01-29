from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    username: Mapped[str]
    used_storage: Mapped[int] = mapped_column(BigInteger, default=0)
    storage_quota_bytes: Mapped[int] = mapped_column(
        BigInteger, 
        default=15 * 1024 ** 3
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    

class Files(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    filename: Mapped[str]
    filepath: Mapped[str]
    storage_key: Mapped[str]
    size: Mapped[int] = mapped_column(BigInteger)
    mime_type: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

class Folders(Base):
    __tablename__ = "folders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str]
    full_path: Mapped[str]
    parent_folder_id: Mapped[int | None] = mapped_column(ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)