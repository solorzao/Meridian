import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Trade, TradeStrategyTag
from app.models.trade_schemas import CreateTradeRequest, TradeResponse, UpdateTradeRequest


def _map_trade_to_response(trade: Trade) -> TradeResponse:
    strategy_names = []
    if trade.strategy_tags:
        for tag in trade.strategy_tags:
            name = tag.strategy.name if tag.strategy else "Unknown"
            strategy_names.append(name)
    return TradeResponse(
        id=str(trade.id),
        ticker=trade.ticker,
        direction=trade.direction,
        entry_date=trade.entry_date,
        entry_price=trade.entry_price,
        exit_date=trade.exit_date,
        exit_price=trade.exit_price,
        position_size=trade.position_size,
        stop_loss=trade.stop_loss,
        take_profit=trade.take_profit,
        pnl=trade.pnl,
        pnl_percent=trade.pnl_percent,
        status=trade.status,
        entry_thesis=trade.entry_thesis,
        exit_thesis=trade.exit_thesis,
        market_sentiment=trade.market_sentiment,
        emotional_state=trade.emotional_state,
        market_conditions=trade.market_conditions,
        notes=trade.notes,
        strategy_tags=strategy_names,
        created_at=trade.created_at,
        updated_at=trade.updated_at,
    )


def _trade_query():
    return select(Trade).options(
        selectinload(Trade.strategy_tags).selectinload(TradeStrategyTag.strategy)
    )


async def get_trades(
    db: AsyncSession,
    user_id: uuid.UUID,
    status: str | None = None,
    skip: int = 0,
    take: int = 50,
) -> list[TradeResponse]:
    query = _trade_query().where(Trade.user_id == user_id)
    if status:
        query = query.where(Trade.status == status)
    query = query.order_by(Trade.entry_date.desc()).offset(skip).limit(take)
    result = await db.execute(query)
    return [_map_trade_to_response(t) for t in result.scalars().all()]


async def get_trade(
    db: AsyncSession, trade_id: uuid.UUID, user_id: uuid.UUID
) -> TradeResponse | None:
    query = _trade_query().where(Trade.id == trade_id, Trade.user_id == user_id)
    result = await db.execute(query)
    trade = result.scalar_one_or_none()
    return _map_trade_to_response(trade) if trade else None


async def create_trade(
    db: AsyncSession, user_id: uuid.UUID, dto: CreateTradeRequest
) -> TradeResponse:
    trade_id = uuid.uuid4()
    now = datetime.utcnow()
    trade = Trade(
        id=trade_id,
        user_id=user_id,
        ticker=dto.ticker.upper(),
        direction=dto.direction,
        entry_date=dto.entry_date,
        entry_price=dto.entry_price,
        position_size=dto.position_size,
        stop_loss=dto.stop_loss,
        take_profit=dto.take_profit,
        entry_thesis=dto.entry_thesis,
        exit_thesis=dto.exit_thesis,
        market_sentiment=dto.market_sentiment,
        emotional_state=dto.emotional_state,
        market_conditions=dto.market_conditions,
        notes=dto.notes,
        status="Open",
        created_at=now,
        updated_at=now,
    )

    if dto.strategy_ids:
        for sid in dto.strategy_ids:
            trade.strategy_tags.append(
                TradeStrategyTag(trade_id=trade_id, strategy_id=uuid.UUID(sid), source="user")
            )

    db.add(trade)
    await db.commit()

    # Re-fetch with relationships loaded
    return await get_trade(db, trade_id, user_id)  # type: ignore


async def update_trade(
    db: AsyncSession, trade_id: uuid.UUID, user_id: uuid.UUID, dto: UpdateTradeRequest
) -> TradeResponse:
    query = _trade_query().where(Trade.id == trade_id, Trade.user_id == user_id)
    result = await db.execute(query)
    trade = result.scalar_one_or_none()
    if not trade:
        raise ValueError(f"Trade {trade_id} not found")

    if dto.exit_date is not None:
        trade.exit_date = dto.exit_date
    if dto.exit_price is not None:
        trade.exit_price = dto.exit_price
    if dto.stop_loss is not None:
        trade.stop_loss = dto.stop_loss
    if dto.take_profit is not None:
        trade.take_profit = dto.take_profit
    if dto.status is not None:
        trade.status = dto.status
    if dto.entry_thesis is not None:
        trade.entry_thesis = dto.entry_thesis
    if dto.exit_thesis is not None:
        trade.exit_thesis = dto.exit_thesis
    if dto.market_sentiment is not None:
        trade.market_sentiment = dto.market_sentiment
    if dto.emotional_state is not None:
        trade.emotional_state = dto.emotional_state
    if dto.market_conditions is not None:
        trade.market_conditions = dto.market_conditions
    if dto.notes is not None:
        trade.notes = dto.notes

    # Replace strategy tags if provided
    if dto.strategy_ids is not None:
        trade.strategy_tags.clear()
        for sid in dto.strategy_ids:
            trade.strategy_tags.append(
                TradeStrategyTag(trade_id=trade.id, strategy_id=uuid.UUID(sid), source="user")
            )

    # Calculate P&L when exit price exists and trade is closed
    if trade.exit_price is not None and trade.status == "Closed":
        multiplier = Decimal(1) if trade.direction == "Long" else Decimal(-1)
        trade.pnl = (trade.exit_price - trade.entry_price) * trade.position_size * multiplier
        if trade.entry_price != 0:
            trade.pnl_percent = (
                (trade.exit_price - trade.entry_price) / trade.entry_price * 100 * multiplier
            )
        else:
            trade.pnl_percent = Decimal(0)

    trade.updated_at = datetime.utcnow()
    await db.commit()

    return await get_trade(db, trade_id, user_id)  # type: ignore


async def delete_trade(db: AsyncSession, trade_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    query = select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id)
    result = await db.execute(query)
    trade = result.scalar_one_or_none()
    if not trade:
        return False
    await db.delete(trade)
    await db.commit()
    return True


async def get_trade_count(db: AsyncSession, user_id: uuid.UUID, status: str | None = None) -> int:
    query = select(func.count()).select_from(Trade).where(Trade.user_id == user_id)
    if status:
        query = query.where(Trade.status == status)
    result = await db.execute(query)
    return result.scalar_one()
