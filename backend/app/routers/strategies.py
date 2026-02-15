import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_id
from app.db.database import get_db
from app.models.strategy_schemas import CreateStrategyRequest, StrategyResponse
from app.services import strategy_service

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategyResponse], response_model_by_alias=True)
async def list_strategies(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await strategy_service.get_strategies(db, user_id)


@router.get("/{strategy_id}", response_model=StrategyResponse, response_model_by_alias=True)
async def get_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    strategy = await strategy_service.get_strategy(db, strategy_id, user_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.post("", response_model=StrategyResponse, status_code=201, response_model_by_alias=True)
async def create_strategy(
    dto: CreateStrategyRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    return await strategy_service.create_strategy(db, user_id, dto)


@router.delete("/{strategy_id}", status_code=204)
async def delete_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    deleted = await strategy_service.delete_strategy(db, strategy_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Strategy not found")
