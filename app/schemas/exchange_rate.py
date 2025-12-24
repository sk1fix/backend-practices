from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel


class ReadExchangeRateDTO(BaseModel):
    id: int
    base_currency_id: int
    target_currency_id: int
    rate: Decimal
    source: str
    updated_at: datetime


class CreateExchangeRateDTO(BaseModel):
    base_currency_id: int
    target_currency_id: int
    rate: Decimal
    source: str

class UpdateExchangeRateDTO(BaseModel):
    rate: Decimal
    source: str
