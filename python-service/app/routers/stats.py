from fastapi import APIRouter

from app.services import stats_service
from app.models.stats_schemas import TradeInput, PerformanceResponse

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.post("/performance", response_model=PerformanceResponse)
async def calculate_performance(trades: list[TradeInput]):
    """Calculate performance statistics from trade data."""
    return stats_service.calculate(trades)
