from datetime import datetime

from app.models.base import CamelModel


class CreateStrategyRequest(CamelModel):
    name: str
    description: str | None = None


class StrategyResponse(CamelModel):
    id: str
    name: str
    description: str | None = None
    source: str
    created_at: datetime
    trade_count: int
