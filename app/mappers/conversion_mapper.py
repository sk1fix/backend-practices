from schemas.conversion import CurrencyConversionDto


def map_orm_to_dto(
        code,
        new_rate,
        new_amount,
        converted) -> CurrencyConversionDto:
    dto = CurrencyConversionDto(
        base_currency=code[:3],
        target_currency=code[3:],
        rate=new_rate,
        amount=new_amount,
        converted_amount=converted)
    return dto
