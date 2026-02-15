import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """Start the background job scheduler with cron triggers."""
    # Jobs would be registered here with cron triggers
    # Example: scheduler.add_job(daily_summary.execute, 'cron', hour=16, minute=30, args=[user_id])
    # For now, the scheduler starts empty — jobs are added via API or on-demand

    scheduler.start()
    logger.info("Background job scheduler started")


def shutdown_scheduler() -> None:
    """Shutdown the scheduler gracefully."""
    scheduler.shutdown(wait=False)
    logger.info("Background job scheduler shut down")
