from pydantic import BaseModel


class IndicatorRequest(BaseModel):
    """Request to calculate indicators."""

    ticker: str
    period: str = "1y"
    interval: str = "1d"
    indicators: list[str] = ["sma_20", "sma_50", "rsi_14", "macd"]


class IndicatorBar(BaseModel):
    """OHLCV bar with indicator values."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    indicators: dict[str, float | None]


class IndicatorResponse(BaseModel):
    """Response with OHLCV and indicator data."""

    ticker: str
    bars: list[IndicatorBar]
    indicators_calculated: list[str]
