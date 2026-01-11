from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_conversion_service
from schemas.conversion import CurrencyConversionDto
from services.currency_conversion import CurrencyConversionService

conversion_route = APIRouter(tags=["Conversion Endpoints"])


@conversion_route.get(
    "/conversion",
    summary="Get conversion",
    tags=["Conversion Endpoints"]
)
async def get_conversion(
    base: str = Query(alias='from'),
    target: str = Query(alias='to'),
    amount: float = Query(alias='amount'),
    service: CurrencyConversionService = Depends(
        get_conversion_service
    )
) -> CurrencyConversionDto:
    result = await service.currency_converter(base, target, amount)
    return result
