from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from api.controllers.currencies import currencies_route
from api.controllers.exchange_rates import exchange_rates_route
from api.controllers.conversion import conversion_route
from core.config import settings
from core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CurrencyAPI turned on")
    yield 
    logger.info("CurrencyAPI turned down")

currency_app = FastAPI(lifespan=lifespan)

currency_app.include_router(currencies_route)
currency_app.include_router(exchange_rates_route)
currency_app.include_router(conversion_route)

if __name__ == "__main__":
    uvicorn.run(
        "main:currency_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )