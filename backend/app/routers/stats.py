from fastapi import APIRouter

from app.models.stats_schemas import PerformanceResponse, TradeInput
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.post("/performance", response_model=PerformanceResponse)
async def calculate_performance(trades: list[TradeInput]):
    """Calculate performance statistics from trade data."""
    return stats_service.calculate(trades)
