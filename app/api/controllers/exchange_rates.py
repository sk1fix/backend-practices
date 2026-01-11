from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from api.dependencies import get_exchange_rate_service
from schemas.exchange_rate import (ReadExchangeRateDTO,
                                   CreateExchangeRateDTO,
                                   UpdateExchangeRateDTO)
from services.exchange_service import ExchangeRateService

exchange_rates_route = APIRouter(tags=["Exchange rates Endpoints"])


@exchange_rates_route.get(
    "/exchange_rates",
    summary="Get all exchange rates",
    tags=["Exchange rates Endpoints"]
)
async def get_exchange_rates(
    service: ExchangeRateService = Depends(get_exchange_rate_service)
) -> list[ReadExchangeRateDTO]:
    result = await service.get_all()
    return result


@exchange_rates_route.post(
    "/exchange_rates",
    summary="Create new exchange rate",
    tags=["Exchange rates Endpoints"]
)
async def create_exchange_rate(
    data: CreateExchangeRateDTO,
    service: ExchangeRateService = Depends(get_exchange_rate_service)
) -> ReadExchangeRateDTO:
    result = await service.create(data)
    return result


@exchange_rates_route.get(
    "/exchange_rates/{exchange_rate_code}",
    summary="Get exchange rate by code",
    tags=["Exchange rates Endpoints"]
)
async def get_exchange_rate_by_code(
    code: str,
    service: ExchangeRateService = Depends(get_exchange_rate_service)
) -> ReadExchangeRateDTO:
    result = await service.get_by_code(code)
    return result


@exchange_rates_route.patch(
    "/exchange_rates/{exchange_rate_code}",
    summary="Update exchange rate",
    tags=["Exchange rates Endpoints"]
)
async def update_exchange_rate(
    exchange_rate_code: Annotated[str, Path(max_length=6, min_length=6)],
    data: UpdateExchangeRateDTO,
    service: ExchangeRateService = Depends(get_exchange_rate_service)
) -> ReadExchangeRateDTO | None:
    result = await service.update(exchange_rate_code, data)
    return result


@exchange_rates_route.delete(
    "/exchange_rates/{exchange_rate_id}",
    summary="Delete exchange rate by id",
    tags=["Exchange rates Endpoints"]
)
async def delete_exchange_rate(
    exchange_rate_id: int,
    service: ExchangeRateService = Depends(get_exchange_rate_service)
) -> bool:
    result = await service.delete(exchange_rate_id)
    return result
