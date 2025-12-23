from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from repositories.currency_repository import CurrencyRepository
from repositories.exchange_rate_repository import ExchangeRateRepository
from services.currency_service import CurrencyService
from services.exchange_service import ExchangeRateService

async def get_currency_repository(session: AsyncSession = Depends(get_db)):
    return CurrencyRepository(session)

async def get_exchange_rate_repository(session: AsyncSession = Depends(get_db)):
    return ExchangeRateRepository(session)

async def get_currency_service(db: AsyncSession = Depends(get_db)) -> CurrencyService:
    repo = CurrencyRepository(db)
    return CurrencyService(repo)

async def get_currency_service(db: AsyncSession = Depends(get_db)) -> ExchangeRateService:
    repo = ExchangeRateRepository(db)
    return ExchangeRateService(repo)