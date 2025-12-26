from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_currency_service
from schemas.currency import ReadCurrencyDTO, CreateUpdateCurrencyDTO
from services.currency_service import CurrencyService

currencies_route = APIRouter(tags=["Currencies Endpoints"])


@currencies_route.get("/currencies",
                      summary="Get all currencies",
                      tags=["Currencies Endpoints"])
async def get_currencies(
        service: CurrencyService = Depends(get_currency_service)
) -> List[ReadCurrencyDTO]:
    result = await service.get_all()
    return result


@currencies_route.post("/currencies",
                       summary="Create new currency",
                       tags=["Currencies Endpoints"])
async def create_currency(
        data: CreateUpdateCurrencyDTO,
        service: CurrencyService = Depends(get_currency_service)
) -> ReadCurrencyDTO:
    result = await service.create(data)
    return result


@currencies_route.get("/currencies/{currency_code}",
                      summary="Get currency by code",
                      tags=["Currencies Endpoints"])
async def get_currency_by_code(
        code: str,
        service: CurrencyService = Depends(get_currency_service)
) -> ReadCurrencyDTO:
    result = await service.get_by_code(code)
    return result


@currencies_route.patch("/currencies/{id}",
                        summary="Update currency",
                        tags=["Currencies Endpoints"])
async def update_currency(
        id: int,
        data: CreateUpdateCurrencyDTO,
        service: CurrencyService = Depends(get_currency_service)) -> bool:
    result = await service.update(id, data)
    return result


@currencies_route.delete("/currencies/{currency_id}",
                         summary="Delete currency by id",
                         tags=["Currencies Endpoints"])
async def get_currency_by_code(
        currency_id: int,
        service: CurrencyService = Depends(get_currency_service)) -> bool:
    result = await service.delete(currency_id)
    return result
