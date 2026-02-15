from fastapi import APIRouter, HTTPException

from app.models.screener_schemas import ScreenerRequest, ScreenerResponse
from app.services import screener_service

router = APIRouter(prefix="/screen", tags=["Screener"])


@router.post("", response_model=ScreenerResponse)
async def run_screener(request: ScreenerRequest):
    """Run stock screener with given criteria."""
    try:
        return screener_service.screen(
            criteria=request.criteria,
            universe=request.universe,
            custom_tickers=request.custom_tickers,
            limit=request.limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screener error: {str(e)}")
