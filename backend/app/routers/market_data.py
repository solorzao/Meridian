from fastapi import APIRouter, HTTPException

from app.models.schemas import OHLCVResponse, QuoteResponse
from app.services import market_data_service

router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.get("/quote/{ticker}", response_model=QuoteResponse)
async def get_quote(ticker: str):
    """Get current quote for a ticker."""
    try:
        return market_data_service.get_quote(ticker)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{ticker}", response_model=OHLCVResponse)
async def get_ohlcv(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
):
    """Get OHLCV data for a ticker."""
    try:
        return market_data_service.get_ohlcv(ticker, period, interval)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
