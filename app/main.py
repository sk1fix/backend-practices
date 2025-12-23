from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from api.controllers.currencies import currencies_route
from core.config import settings 
from core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DepositAPI turned on")
    yield 
    logger.info("DepositAPI turned down")


deposit_app = FastAPI(lifespan=lifespan)

deposit_app.include_router(currencies_route)

@deposit_app.get("/")
def root():
    return {"msg" : "Welcome to CurrenciesAPI"}

if __name__ == "__main__":
    uvicorn.run(
        "main:deposit_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )