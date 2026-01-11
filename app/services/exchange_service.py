from mappers.exchange_rate_mapper import map_orm_to_dto
from schemas.exchange_rate import ReadExchangeRateDTO, UpdateExchangeRateDTO, CreateExchangeRateDTO


class ExchangeRateService:
    def __init__(self, repo) -> None:
        self.repo = repo

    async def get_all(self) -> list[ReadExchangeRateDTO]:
        result = await self.repo.get_exchange_rates()
        return [map_orm_to_dto(i) for i, j, k in result]

    async def get_by_code(self, code: str) -> ReadExchangeRateDTO | None:
        result = await self.repo.get_exchange_rates_by_pair(code)
        if result is None:
            return None
        dto = map_orm_to_dto(result[0])
        return dto

    async def create(
        self,
        data: CreateExchangeRateDTO
    ) -> ReadExchangeRateDTO | None:
        result = await self.repo.create_exchange_rates(data)
        if result is None:
            return None
        dto = map_orm_to_dto(result[0])
        return dto

    async def update(
        self,
        id: int,
        data: UpdateExchangeRateDTO
    ) -> ReadExchangeRateDTO | None:
        result = await self.repo.update_exchange_rate(id, data)
        if result is None:
            return None
        dto = map_orm_to_dto(result)
        return dto

    async def delete(self, id: int) -> bool:
        result = await self.repo.delete_exchange_rates(id)
        return result
