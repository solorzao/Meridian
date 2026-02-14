import logging
import uuid

from sqlalchemy import select

from app.db.database import async_session
from app.db.models import Trade

logger = logging.getLogger(__name__)


async def execute(trade_id: uuid.UUID, user_id: uuid.UUID) -> None:
    logger.info("Generating embedding for trade %s", trade_id)

    async with async_session() as db:
        result = await db.execute(
            select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id)
        )
        trade = result.scalar_one_or_none()

        if not trade:
            logger.warning("Trade %s not found for embedding", trade_id)
            return

    # Build text representation for embedding
    trade_text = f"{trade.ticker} {trade.direction} trade. "
    trade_text += f"Entry: ${trade.entry_price:.2f} on {trade.entry_date:%Y-%m-%d}. "
    if trade.exit_price is not None:
        trade_text += f"Exit: ${trade.exit_price:.2f} on {trade.exit_date:%Y-%m-%d}. "
    if trade.pnl is not None:
        trade_text += f"P&L: ${trade.pnl:.2f}. "
    if trade.thesis:
        trade_text += f"Thesis: {trade.thesis}. "
    if trade.notes:
        trade_text += f"Notes: {trade.notes}."

    # TODO: Call Azure OpenAI embeddings API and store vector

    logger.info("Embedding generated for trade %s (%d chars)", trade_id, len(trade_text))
