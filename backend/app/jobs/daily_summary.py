import logging
import uuid

from sqlalchemy import select

from app.db.database import async_session
from app.db.models import Trade
from app.services.market_data import market_data_service

logger = logging.getLogger(__name__)


async def execute(user_id: uuid.UUID) -> None:
    logger.info("Generating daily summary for user %s", user_id)

    async with async_session() as db:
        result = await db.execute(
            select(Trade).where(Trade.user_id == user_id, Trade.status == "Open").limit(100)
        )
        open_trades = list(result.scalars().all())

        if not open_trades:
            logger.info("No open trades for user %s, skipping summary", user_id)
            return

        for trade in open_trades:
            try:
                quote = market_data_service.get_quote(trade.ticker)
                if trade.direction == "Long":
                    unrealized_pnl = (quote.price - float(trade.entry_price)) * float(
                        trade.position_size
                    )
                else:
                    unrealized_pnl = (float(trade.entry_price) - quote.price) * float(
                        trade.position_size
                    )

                logger.info(
                    "Position %s: Entry $%.2f, Current $%.2f, Unrealized P&L: $%.2f",
                    trade.ticker,
                    trade.entry_price,
                    quote.price,
                    unrealized_pnl,
                )
            except Exception as e:
                logger.warning("Failed to fetch quote for %s: %s", trade.ticker, e)

    # TODO: Format summary and send via email/notification
