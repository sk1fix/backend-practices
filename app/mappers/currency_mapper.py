from schemas.currency import ReadCurrencyDTO


def map_orm_to_dto(entity):
    dto = ReadCurrencyDTO(
        id=entity.id,
        code=entity.code,
        fullname=entity.fullname,
        sign=entity.sign,
        is_base=entity.is_base
    )
    return dto
