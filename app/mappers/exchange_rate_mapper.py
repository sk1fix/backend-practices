from schemas.exchange_rate import ReadExchangeRateDTO


def map_orm_to_dto(entity):
    dto = ReadExchangeRateDTO(
        id=entity.id,
        base_currency_id=entity.base_currency_id,
        target_currency_id=entity.target_currency_id,
        rate=entity.rate,
        source=entity.source,
        updated_at=entity.updated_at
    )
    return dto
