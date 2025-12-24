from mappers.currency_mapper import map_orm_to_dto


class CurrencyService:
    def __init__(self, repo):
        self.repo = repo

    async def get_all(self):
        result = await self.repo.get_currencies()
        list_dto = []
        for row in result:
            dto = map_orm_to_dto(row)
            list_dto.append(dto)
        return list_dto

    async def get_by_code(self, code):
        result = await self.repo.get_currency_by_code(code)
        dto = map_orm_to_dto(result)
        return dto

    async def create(self, data):
        result = await self.repo.create_currency(data)
        dto = map_orm_to_dto(result)
        return dto

    async def update(self, id, data):
        result = await self.repo.update_currency(id, data)
        return result

    async def delete(self, id):
        result = await self.repo.delete_currency(id)
        return result
