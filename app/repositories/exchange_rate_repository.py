from typing import List, Tuple, Any

from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session, aliased

from models.models import ExchangeRates, Currencies
from schemas.exchange_rate import CreateExchangeRateDTO, UpdateExchangeRateDTO


class ExchangeRateRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def get_exchange_rates(
            self
    ) -> List[Tuple[ExchangeRates, str, str]]:
        BaseCurrency = aliased(Currencies)
        TargetCurrency = aliased(Currencies)
        async with self.session as session:
            query = (
                select(
                    ExchangeRates,
                    BaseCurrency.code,
                    TargetCurrency.code
                )
                .join(BaseCurrency,
                      BaseCurrency.id == ExchangeRates.base_currency_id)
                .join(
                    TargetCurrency,
                    TargetCurrency.id == ExchangeRates.target_currency_id)
            )
            result = await session.execute(query)

            return result.all()

    async def get_exchange_rates_by_pair(self,
                                         pair: str
                                         ) -> Tuple[ExchangeRates, str, str]:
        BaseCurrency = aliased(Currencies)
        TargetCurrency = aliased(Currencies)
        async with self.session as session:
            query = (
                select(
                    ExchangeRates,
                    BaseCurrency.code,
                    TargetCurrency.code
                )
                .join(BaseCurrency,
                      BaseCurrency.id == ExchangeRates.base_currency_id)
                .join(
                    TargetCurrency,
                    TargetCurrency.id == ExchangeRates.target_currency_id)
                .where(
                    pair[:3] == BaseCurrency.code,
                    pair[3:] == TargetCurrency.code)
            )
            result = await session.execute(query)

            return result.first()

    async def create_exchange_rates(self,
                                    data: CreateExchangeRateDTO
                                    ) -> Tuple[ExchangeRates, str, str]:
        async with self.session as session:
            exchange_rate = ExchangeRates(**data.model_dump())
            session.add(exchange_rate)
            await session.commit()
            await session.refresh(exchange_rate)

            BaseCurrency = aliased(Currencies)
            TargetCurrency = aliased(Currencies)

            query = (
                select(
                    ExchangeRates,
                    BaseCurrency.code,
                    TargetCurrency.code,
                )
                .join(BaseCurrency,
                      BaseCurrency.id == ExchangeRates.base_currency_id)
                .join(TargetCurrency,
                      TargetCurrency.id == ExchangeRates.target_currency_id)
                .where(ExchangeRates.id == exchange_rate.id)
            )
            result = await session.execute(query)
            row = result.first()
            return row

    async def update_exchange_rate(self,
                                   pair: str,
                                   data: UpdateExchangeRateDTO
                                   ) -> ExchangeRates | Any:
        BaseCurrency = aliased(Currencies)
        TargetCurrency = aliased(Currencies)

        async with self.session as session:
            stmt = (
                select(ExchangeRates)
                .join(BaseCurrency,
                      BaseCurrency.id == ExchangeRates.base_currency_id)
                .join(TargetCurrency,
                      TargetCurrency.id == ExchangeRates.target_currency_id)
                .where(
                    BaseCurrency.code == pair[:3],
                    TargetCurrency.code == pair[3:],
                )
            )
            result = await session.execute(stmt)
            exchange_rate: ExchangeRates | None = result.scalars().first()

            if exchange_rate is None:
                return None

            data_dict = data.model_dump(exclude_unset=True)
            for field, value in data_dict.items():
                setattr(exchange_rate, field, value)

            await session.commit()
            await session.refresh(exchange_rate)

            return exchange_rate

    async def delete_exchange_rates(self, id: int) -> bool:
        async with self.session as session:
            query = delete(ExchangeRates).where(id == ExchangeRates.id)
            await session.execute(query)
            await session.commit()

            return True
