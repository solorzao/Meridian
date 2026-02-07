from pydantic import BaseModel
from typing import Literal


class RangeCriteria(BaseModel):
    """Numeric range criteria."""

    min: float | None = None
    max: float | None = None


class ScreenerCriteria(BaseModel):
    """Criteria for screening stocks."""

    # Price criteria
    price: RangeCriteria | None = None
    gap_percent: RangeCriteria | None = None

    # Volume criteria
    volume_ratio: RangeCriteria | None = None  # vs 20-day avg
    min_volume: int | None = None

    # Technical criteria
    rsi_14: RangeCriteria | None = None
    above_sma_20: bool | None = None
    above_sma_50: bool | None = None
    above_sma_200: bool | None = None

    # Filters
    sectors: list[str] | None = None
    market_cap_min: int | None = None
    market_cap_max: int | None = None


class ScreenerRequest(BaseModel):
    """Request to run screener."""

    criteria: ScreenerCriteria
    universe: Literal["sp500", "nasdaq100", "custom"] = "sp500"
    custom_tickers: list[str] | None = None
    limit: int = 20


class ScreenerMatch(BaseModel):
    """A stock matching screener criteria."""

    ticker: str
    name: str | None = None
    price: float
    change_percent: float
    volume: int
    volume_ratio: float | None = None
    rsi_14: float | None = None
    gap_percent: float | None = None
    sector: str | None = None
    market_cap: int | None = None


class ScreenerResponse(BaseModel):
    """Screener results."""

    matches: list[ScreenerMatch]
    total_scanned: int
    criteria_summary: str
