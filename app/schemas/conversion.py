from pydantic import BaseModel


class CurrencyConversionDto(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    amount: float
    converted_amount: float
