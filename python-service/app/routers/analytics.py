import re

from fastapi import APIRouter, HTTPException, Request

from app.middleware.rate_limiter import limiter
from app.models.indicator_schemas import IndicatorRequest, IndicatorResponse
from app.models.schemas import OHLCVResponse, QuoteResponse
from app.models.screener_schemas import ScreenerRequest, ScreenerResponse
from app.services.indicators import indicator_service
from app.services.market_data import market_data_service
from app.services.screener import screener_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

TICKER_PATTERN = re.compile(r"^[A-Za-z0-9\-\.]{1,10}$")


def _validate_ticker(ticker: str) -> str:
    if not TICKER_PATTERN.match(ticker):
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker. Must be 1-10 alphanumeric characters.",
        )
    return ticker.upper()


@router.get("/quote/{ticker}", response_model=QuoteResponse)
async def get_quote(ticker: str):
    ticker = _validate_ticker(ticker)
    return market_data_service.get_quote(ticker)


@router.get("/ohlcv/{ticker}", response_model=OHLCVResponse)
async def get_ohlcv(ticker: str, period: str = "1y", interval: str = "1d"):
    ticker = _validate_ticker(ticker)
    return market_data_service.get_ohlcv(ticker, period, interval)


@router.post("/indicators", response_model=IndicatorResponse)
async def calculate_indicators(request: IndicatorRequest):
    return indicator_service.calculate(
        request.ticker, request.period, request.interval, request.indicators
    )


@router.post("/screen", response_model=ScreenerResponse)
@limiter.limit("5/minute")
async def run_screener(http_request: Request, request: ScreenerRequest):
    return screener_service.screen(
        request.criteria, request.universe, request.custom_tickers, request.limit
    )
