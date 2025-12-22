from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel


class ReadExchangeRateDTO(BaseModel):
    id: int
    base_currency_code: str
    target_currency_code: str
    rate: Decimal
    source: str
    updated_at: datetime


class CreateUpdateExchangeRateDTO(BaseModel):
    base_currency_code: str
    target_currency_code: str
    rate: Decimal
    source: str
