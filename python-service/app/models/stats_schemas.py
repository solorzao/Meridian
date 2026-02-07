from pydantic import BaseModel
from datetime import datetime


class TradeInput(BaseModel):
    """Trade data for statistics calculation."""

    id: str
    ticker: str
    direction: str  # "long" or "short"
    entry_date: datetime
    entry_price: float
    exit_date: datetime | None = None
    exit_price: float | None = None
    position_size: float
    pnl: float | None = None
    strategy_tags: list[str] = []


class PerformanceStats(BaseModel):
    """Overall performance statistics."""

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_hold_days: float
    expectancy: float


class StrategyStats(BaseModel):
    """Performance statistics for a single strategy."""

    strategy_name: str
    total_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    avg_pnl: float


class PerformanceResponse(BaseModel):
    """Full performance analysis response."""

    overall: PerformanceStats
    by_strategy: list[StrategyStats]
    by_ticker: dict[str, PerformanceStats]
    monthly_pnl: dict[str, float]  # "2026-01": 1234.56
