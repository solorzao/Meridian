import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_id
from app.db.database import get_db
from app.models.trade_schemas import CreateTradeRequest, TradeResponse, UpdateTradeRequest
from app.services import trade_service

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("", response_model=list[TradeResponse], response_model_by_alias=True)
async def list_trades(
    status: str | None = None,
    skip: int = 0,
    take: int = 50,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await trade_service.get_trades(db, user_id, status, skip, take)


@router.get("/{trade_id}", response_model=TradeResponse, response_model_by_alias=True)
async def get_trade(
    trade_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    trade = await trade_service.get_trade(db, trade_id, user_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.post("", response_model=TradeResponse, status_code=201, response_model_by_alias=True)
async def create_trade(
    dto: CreateTradeRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await trade_service.create_trade(db, user_id, dto)


@router.put("/{trade_id}", response_model=TradeResponse, response_model_by_alias=True)
async def update_trade(
    trade_id: uuid.UUID,
    dto: UpdateTradeRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    try:
        return await trade_service.update_trade(db, trade_id, user_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{trade_id}", status_code=204)
async def delete_trade(
    trade_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    deleted = await trade_service.delete_trade(db, trade_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trade not found")
