from datetime import datetime
from pydantic import BaseModel


class OHLCVBar(BaseModel):
    """Single OHLCV bar."""

    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class OHLCVResponse(BaseModel):
    """OHLCV data response."""

    ticker: str
    bars: list[OHLCVBar]
    period: str
    interval: str


class QuoteResponse(BaseModel):
    """Current quote response."""

    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime


class MarketDataError(BaseModel):
    """Error response for market data."""

    error: str
    ticker: str
