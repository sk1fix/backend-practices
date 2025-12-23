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


class CreateExchangeRateDTO(BaseModel):
    base_currency_code: str
    target_currency_code: str
    rate: Decimal
    source: str

class UpdateExchangeRateDTO(BaseModel):
    rate: Decimal
    source: str
