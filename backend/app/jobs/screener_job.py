import logging

from sqlalchemy import select

from app.db.database import async_session
from app.db.models import AgentConfig
from app.models.screener_schemas import ScreenerCriteria
from app.services.screener import screener_service

logger = logging.getLogger(__name__)


async def execute(user_id_str: str) -> None:
    logger.info("Running screener job for user %s", user_id_str)

    async with async_session() as db:
        result = await db.execute(
            select(AgentConfig).where(
                AgentConfig.user_id == user_id_str,
                AgentConfig.agent_type == "screener",
            )
        )
        config = result.scalar_one_or_none()

        if not config or not config.is_enabled:
            logger.info("Screener not configured or disabled for user %s", user_id_str)
            return

    results = screener_service.screen(ScreenerCriteria(), "sp500", None, 20)
    logger.info("Screener found %d matches for user %s", len(results.matches), user_id_str)

    # TODO: Store results and notify user
