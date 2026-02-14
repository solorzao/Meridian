import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Strategy, TradeStrategyTag
from app.models.strategy_schemas import CreateStrategyRequest, StrategyResponse


def _map_strategy_to_response(strategy: Strategy, trade_count: int = 0) -> StrategyResponse:
    return StrategyResponse(
        id=str(strategy.id),
        name=strategy.name,
        description=strategy.description,
        source=strategy.source,
        created_at=strategy.created_at,
        trade_count=trade_count,
    )


async def get_strategies(db: AsyncSession, user_id: uuid.UUID) -> list[StrategyResponse]:
    # Get strategies with trade counts
    query = (
        select(Strategy, func.count(TradeStrategyTag.trade_id).label("trade_count"))
        .outerjoin(TradeStrategyTag, Strategy.id == TradeStrategyTag.strategy_id)
        .where(Strategy.user_id == user_id)
        .group_by(Strategy.id)
        .order_by(Strategy.name)
    )
    result = await db.execute(query)
    return [_map_strategy_to_response(row[0], row[1]) for row in result.all()]


async def get_strategy(
    db: AsyncSession, strategy_id: uuid.UUID, user_id: uuid.UUID
) -> StrategyResponse | None:
    query = (
        select(Strategy, func.count(TradeStrategyTag.trade_id).label("trade_count"))
        .outerjoin(TradeStrategyTag, Strategy.id == TradeStrategyTag.strategy_id)
        .where(Strategy.id == strategy_id, Strategy.user_id == user_id)
        .group_by(Strategy.id)
    )
    result = await db.execute(query)
    row = result.one_or_none()
    return _map_strategy_to_response(row[0], row[1]) if row else None


async def create_strategy(
    db: AsyncSession, user_id: uuid.UUID, dto: CreateStrategyRequest
) -> StrategyResponse:
    strategy = Strategy(
        id=uuid.uuid4(),
        user_id=user_id,
        name=dto.name,
        description=dto.description,
        source="user",
        created_at=datetime.utcnow(),
    )
    db.add(strategy)
    await db.commit()
    return _map_strategy_to_response(strategy, 0)


async def delete_strategy(db: AsyncSession, strategy_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    query = select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == user_id)
    result = await db.execute(query)
    strategy = result.scalar_one_or_none()
    if not strategy:
        return False
    await db.delete(strategy)
    await db.commit()
    return True
