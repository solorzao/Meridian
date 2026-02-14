import logging
import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import async_session
from app.db.models import Trade, TradeStrategyTag, UserProfile

logger = logging.getLogger(__name__)


async def execute(user_id: uuid.UUID, user_id_str: str) -> None:
    logger.info("Refreshing trading profile for user %s", user_id)

    async with async_session() as db:
        result = await db.execute(
            select(Trade)
            .options(selectinload(Trade.strategy_tags).selectinload(TradeStrategyTag.strategy))
            .where(Trade.user_id == user_id, Trade.status == "Closed")
            .limit(500)
        )
        trades = list(result.scalars().all())

        if not trades:
            return

        # Analyze strategy performance
        strategy_trades = defaultdict(list)
        for trade in trades:
            for tag in trade.strategy_tags or []:
                name = tag.strategy.name if tag.strategy else "Unknown"
                strategy_trades[name].append(trade)

        strategy_performance = {}
        for name, strades in strategy_trades.items():
            wins = sum(1 for t in strades if t.pnl and t.pnl > 0)
            strategy_performance[name] = wins / len(strades) if strades else 0

        # Determine trading style
        hold_days = []
        for t in trades:
            if t.exit_date:
                hold_days.append((t.exit_date - t.entry_date).total_seconds() / 86400)

        avg_hold = sum(hold_days) / len(hold_days) if hold_days else 0

        if avg_hold < 1:
            trading_style = "Day Trader"
        elif avg_hold < 5:
            trading_style = "Swing Trader"
        elif avg_hold < 30:
            trading_style = "Position Trader"
        else:
            trading_style = "Investor"

        # Get most-traded tickers
        ticker_counts = defaultdict(int)
        for t in trades:
            ticker_counts[t.ticker] += 1
        top_tickers = sorted(ticker_counts, key=ticker_counts.get, reverse=True)[:10]

        # Update or create profile
        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id_str)
        )
        profile = profile_result.scalar_one_or_none()

        if not profile:
            profile = UserProfile(user_id=user_id_str)
            db.add(profile)

        profile.trading_style = trading_style
        profile.strategy_performance = strategy_performance
        profile.watchlist_tickers = top_tickers
        profile.last_refreshed = datetime.utcnow()

        await db.commit()

        logger.info(
            "Profile refreshed for user %s: style=%s, strategies=%d",
            user_id,
            trading_style,
            len(strategy_performance),
        )
