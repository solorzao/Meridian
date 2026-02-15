from datetime import datetime
from decimal import Decimal
from typing import Literal

from app.models.base import CamelModel


class CreateTradeRequest(CamelModel):
    ticker: str
    direction: Literal["Long", "Short"]
    entry_date: datetime
    entry_price: Decimal
    position_size: Decimal
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    entry_thesis: str | None = None
    exit_thesis: str | None = None
    market_sentiment: int | None = None
    emotional_state: str | None = None
    market_conditions: str | None = None
    notes: str | None = None
    strategy_ids: list[str] | None = None


class UpdateTradeRequest(CamelModel):
    exit_date: datetime | None = None
    exit_price: Decimal | None = None
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    status: Literal["Open", "Closed", "Cancelled"] | None = None
    entry_thesis: str | None = None
    exit_thesis: str | None = None
    market_sentiment: int | None = None
    emotional_state: str | None = None
    market_conditions: str | None = None
    notes: str | None = None
    strategy_ids: list[str] | None = None


class TradeResponse(CamelModel):
    id: str
    ticker: str
    direction: str
    entry_date: datetime
    entry_price: Decimal
    exit_date: datetime | None = None
    exit_price: Decimal | None = None
    position_size: Decimal
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    pnl: Decimal | None = None
    pnl_percent: Decimal | None = None
    status: str
    entry_thesis: str | None = None
    exit_thesis: str | None = None
    market_sentiment: int | None = None
    emotional_state: str | None = None
    market_conditions: str | None = None
    notes: str | None = None
    strategy_tags: list[str]
    created_at: datetime
    updated_at: datetime
