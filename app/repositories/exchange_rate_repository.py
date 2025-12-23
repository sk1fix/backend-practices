from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session, aliased

from models.models import ExchangeRates, Currencies
from schemas.currency import CreateExchangeRateDTO


class CurrencyRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def get_exchange_rates(self):
        BaseCurrency = aliased(Currencies)
        TargetCurrency = aliased(Currencies)
        async with self.session as session:
            query = (
                select(
                ExchangeRates, BaseCurrency.code, TargetCurrency.code
                )
                .join(BaseCurrency, BaseCurrency.id == ExchangeRates.base_currency_id)
                .join(
                TargetCurrency, TargetCurrency.id == ExchangeRates.target_currency_id)
            )
            result = await session.execute(query)

            return result.all()

    async def get_exchange_rates_by_pair(self, pair):
        BaseCurrency = aliased(Currencies)
        TargetCurrency = aliased(Currencies)
        async with self.session as session:
            query = (
                select(
                ExchangeRates, BaseCurrency.code, TargetCurrency.code
                )
                .join(BaseCurrency, BaseCurrency.id == ExchangeRates.base_currency_id)
                .join(
                TargetCurrency, TargetCurrency.id == ExchangeRates.target_currency_id)
                .where(pair[:3] == BaseCurrency.code, pair[3:] == TargetCurrency.code)
            )
            result = await session.execute(query)

            return result.all()

    async def create_exchange_rates(self, data):
        async with self.session as session:
            exchange_rate = ExchangeRates(**data.model_dump())
            session.add(exchange_rate)
            await session.commit()
            await session.refresh(exchange_rate)

            return exchange_rate

    async def update_exchange_rate(self, pair: str, data):
        BaseCurrency = aliased(Currencies)
        TargetCurrency = aliased(Currencies)

        async with self.session as session:
            stmt = (
                select(ExchangeRates)
                .join(BaseCurrency, BaseCurrency.id == ExchangeRates.base_currency_id)
                .join(TargetCurrency, TargetCurrency.id == ExchangeRates.target_currency_id)
                .where(
                    BaseCurrency.code == pair[:3],
                    TargetCurrency.code == pair[3:],
                )
            )
            result = await session.execute(stmt)
            exchange_rate = result.scalars().first()

            if exchange_rate is None:
                return False  
            data_dict = data.model_dump(exclude_unset=True)
            for field, value in data_dict.items():
                setattr(exchange_rate, field, value)

            await session.commit()
            await session.refresh(exchange_rate)

            return True

    async def delete_exchange_rates(self, id):
        async with self.session as session:
            query = delete(ExchangeRates).where(id == ExchangeRates.id)
            await session.execute(query)
            await session.commit()

            return True
