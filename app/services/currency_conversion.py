from mappers.conversion_mapper import map_orm_to_dto


class CurrencyConversionService:
    def __init__(self, repo):
        self.repo = repo

    async def currency_converter(self, base, target, amount):
        result = await self.repo.get_exchange_rates_by_pair(base+target)
        if result:
            converted = amount * float(result[0].rate)
            return map_orm_to_dto(base+target, result[0].rate, amount, converted)

        result = await self.repo.get_exchange_rates_by_pair(target+base)
        if result:
            new_rate = 1 / float(result[0].rate)
            converted = amount * new_rate
            return map_orm_to_dto(base+target, new_rate, amount, converted)

        result_a = await self.repo.get_exchange_rates_by_pair("USD" + base)
        result_b = await self.repo.get_exchange_rates_by_pair("USD" + target)
        if result_a and result_b:
            new_rate = float(result_b[0].rate) / float(result_a[0].rate)
            converted = amount * new_rate
            return map_orm_to_dto(base+target, new_rate, amount, converted)

        else:
            return None
