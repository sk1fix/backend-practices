from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_currency_service
from schemas.currency import ReadCurrencyDTO, CreateUpdateCurrencyDTO
from services.currency_service import CurrencyService

currencies_route = APIRouter(tags=["Currencies Endpoints"])

@currencies_route.get("/currencies", summary="Get all currencies", tags=["Currencies Endpoints"])
async def get_currencies(service: CurrencyService = Depends(get_currency_service)):
    result = await service.get_all()
    return result

@currencies_route.post("/currencies", summary="Create new currency", tags=["Currencies Endpoints"])
async def create_currencies(data: CreateUpdateCurrencyDTO, service: CurrencyService = Depends(get_currency_service)):
    result = await service.create(data)
    return result