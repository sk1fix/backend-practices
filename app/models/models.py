from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings
from database.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    username: Mapped[str]
    used_storage: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0")
    storage_quota_bytes: Mapped[int] = mapped_column(
        BigInteger,
        default=settings.DEFAULT_QUOTA_BYTES,
        server_default=str(settings.DEFAULT_QUOTA_BYTES),
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow)


class Folders(Base):
    __tablename__ = "folders"
    __table_args__ = (
        UniqueConstraint("user_id", "full_path", name="uq_folders_user_path"),
        Index("ix_folders_user_parent", "user_id", "parent_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str]
    full_path: Mapped[str]
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )


class Files(Base):
    __tablename__ = "files"
    __table_args__ = (
        UniqueConstraint("user_id", "storage_key", name="uq_files_user_key"),
        Index("ix_files_user_folder", "user_id", "folder_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"))
    folder_id: Mapped[int | None] = mapped_column(
        ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    filename: Mapped[str]
    storage_key: Mapped[str]
    size: Mapped[int] = mapped_column(BigInteger)
    mime_type: Mapped[str]
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )
