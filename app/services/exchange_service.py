from mappers.exchange_rate_mapper import map_orm_to_dto


class ExchangeRateService:
    def __init__(self, repo):
        self.repo = repo

    async def get_all(self):
        result = await self.repo.get_exchange_rates()
        list_dto = []
        for row, base, target in result:
            dto = map_orm_to_dto(row, base, target)
            list_dto.append(dto)
        return list_dto

    async def get_by_code(self, code):
        result = await self.repo.get_exchange_rates_by_pair(code)
        if result is None:
            return None
        dto = map_orm_to_dto(result[0], result[1], result[2])
        return dto

    async def create(self, data):
        result = await self.repo.create_exchange_rates(data)
        if result is None:
            return None
        dto = map_orm_to_dto(result[0], result[1], result[2])
        return dto

    async def update(self, id, data):
        result = await self.repo.update_exchange_rate(id, data)
        if result is None:
            return None

        base_currency = await self.currency_repo.get_currency_by_id(result.base_currency_id)
        target_currency = await self.currency_repo.get_currency_by_id(result.target_currency_id)
        dto = map_orm_to_dto(result, base_currency.code, target_currency.code)
        return dto

    async def delete(self, id):
        result = await self.repo.delete_exchange_rates(id)
        return result
