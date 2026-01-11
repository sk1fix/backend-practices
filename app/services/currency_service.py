from mappers.currency_mapper import map_orm_to_dto
from schemas.currency import ReadCurrencyDTO, CreateUpdateCurrencyDTO


class CurrencyService:
    def __init__(self, repo):
        self.repo = repo

    async def get_all(self) -> list[ReadCurrencyDTO]:
        result = await self.repo.get_currencies()
        return [map_orm_to_dto(i) for i in result]

    async def get_by_code(self, code: str) -> ReadCurrencyDTO:
        result = await self.repo.get_currency_by_code(code)
        return map_orm_to_dto(result)

    async def create(self, data: CreateUpdateCurrencyDTO) -> ReadCurrencyDTO:
        result = await self.repo.create_currency(data)
        return map_orm_to_dto(result)

    async def update(self, id: int, data: CreateUpdateCurrencyDTO) -> bool:
        result = await self.repo.update_currency(id, data)
        return result

    async def delete(self, id: int) -> bool:
        result = await self.repo.delete_currency(id)
        return result
