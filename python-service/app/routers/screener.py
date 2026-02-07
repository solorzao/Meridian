from fastapi import APIRouter

from app.services import screener_service
from app.models.screener_schemas import ScreenerRequest, ScreenerResponse

router = APIRouter(prefix="/screen", tags=["Screener"])


@router.post("", response_model=ScreenerResponse)
async def run_screener(request: ScreenerRequest):
    """Run stock screener with given criteria."""
    return screener_service.screen(
        criteria=request.criteria,
        universe=request.universe,
        custom_tickers=request.custom_tickers,
        limit=request.limit,
    )
