from pydantic import BaseModel


class ReadCurrencyDTO(BaseModel):
    id: int
    code: str
    fullname: str
    sign: str
    is_base: bool


class CreateUpdateCurrencyDTO(BaseModel):
    code: str
    fullname: str
    sign: str
    is_base: bool
