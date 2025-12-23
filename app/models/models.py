from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from database.base import Base


class Currencies(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, index=True)
    fullname: Mapped[str] = mapped_column(String(100))
    sign: Mapped[str] = mapped_column(String(8))
    is_base: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class ExchangeRates(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    base_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id", ondelete="CASCADE"))
    target_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id", ondelete="CASCADE"))
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    source: Mapped[str] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
