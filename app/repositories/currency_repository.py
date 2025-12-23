from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from models.models import Currencies


class CurrencyRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def get_currencies(self) -> list[Currencies]:
        async with self.session as session:
            query = select(Currencies)
            result = await session.execute(query)

            return result.scalars().all()

    async def get_currency_by_code(self, code):
        async with self.session as session:
            query = select(Currencies).where(code == Currencies.code)
            result = await session.execute(query)

            return result.scalars().first()

    async def create_currency(self, data):
        async with self.session as session:
            currency = Currencies(**data.model_dump())
            session.add(currency)
            await session.commit()
            await session.refresh(currency)

            return currency

    async def update_currency(self, id, data):
        async with self.session as session:
            query = update(Currencies).where(
                id == Currencies.id).values(**data.model_dump())
            await session.execute(query)
            await session.commit()

            return True

    async def delete_currency(self, id):
        async with self.session as session:
            query = delete(Currencies).where(id == Currencies.id)
            await session.execute(query)
            await session.commit()

            return True
