from fastapi import APIRouter, HTTPException

from app.services import indicator_service
from app.models.indicator_schemas import IndicatorRequest, IndicatorResponse

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.post("", response_model=IndicatorResponse)
async def calculate_indicators(request: IndicatorRequest):
    """Calculate technical indicators for a ticker."""
    try:
        return indicator_service.calculate(
            ticker=request.ticker,
            period=request.period,
            interval=request.interval,
            indicators=request.indicators,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
