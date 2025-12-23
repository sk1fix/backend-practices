from schemas.exchange_rate import ReadExchangeRateDTO


def map_orm_to_dto(entity, base_code, target_code):
    dto = ReadExchangeRateDTO(
        id=entity.id,
        base_currency_code=base_code,
        target_currency_code=target_code,
        rate=entity.rate,
        source=entity.source,
        updated_at=entity.update_at
    )
    return dto
