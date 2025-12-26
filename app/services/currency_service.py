from typing import List

from mappers.currency_mapper import map_orm_to_dto
from schemas.currency import ReadCurrencyDTO, CreateUpdateCurrencyDTO


class CurrencyService:
    def __init__(self, repo):
        self.repo = repo

    async def get_all(self) -> List[ReadCurrencyDTO]:
        result = await self.repo.get_currencies()
        list_dto = []
        for row in result:
            dto = map_orm_to_dto(row)
            list_dto.append(dto)
        return list_dto

    async def get_by_code(self, code: str) -> ReadCurrencyDTO:
        result = await self.repo.get_currency_by_code(code)
        dto = map_orm_to_dto(result)
        return dto

    async def create(self, data: CreateUpdateCurrencyDTO) -> ReadCurrencyDTO:
        result = await self.repo.create_currency(data)
        dto = map_orm_to_dto(result)
        return dto

    async def update(self, id: int, data: CreateUpdateCurrencyDTO) -> bool:
        result = await self.repo.update_currency(id, data)
        return result

    async def delete(self, id: int) -> bool:
        result = await self.repo.delete_currency(id)
        return result
