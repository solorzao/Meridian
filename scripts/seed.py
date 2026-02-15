"""Seed script: creates a test user and sample trades/strategies."""

import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

# Adjust path so we can import app modules
import sys
sys.path.insert(0, "backend")

from app.db.database import async_session, engine  # noqa: E402
from app.db.models import Base, User, Trade, Strategy, TradeStrategyTag  # noqa: E402

TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.id == TEST_USER_ID))
        if result.scalar_one_or_none():
            print("Test user already exists, skipping seed.")
            return

        # Create test user
        user = User(
            id=TEST_USER_ID,
            azure_ad_b2c_id="dev-test-user-001",
            email="dev@meridian.local",
            display_name="Dev User",
            subscription_tier="Free",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)

        # Create strategies
        strategies = []
        for name, desc in [
            ("Breakout", "Price breaks above resistance with volume"),
            ("Mean Reversion", "Buy oversold, sell overbought"),
            ("Momentum", "Follow strong trend direction"),
        ]:
            s = Strategy(
                id=uuid.uuid4(),
                user_id=TEST_USER_ID,
                name=name,
                description=desc,
                source="user",
                created_at=datetime.utcnow(),
            )
            strategies.append(s)
            db.add(s)

        await db.flush()

        # Create sample trades
        now = datetime.utcnow()
        sample_trades = [
            {
                "ticker": "AAPL",
                "direction": "Long",
                "entry_date": now - timedelta(days=10),
                "entry_price": Decimal("185.5000"),
                "position_size": Decimal("50.0000"),
                "stop_loss": Decimal("180.0000"),
                "take_profit": Decimal("195.0000"),
                "status": "Open",
                "thesis": "Strong earnings beat, AI momentum",
            },
            {
                "ticker": "NVDA",
                "direction": "Long",
                "entry_date": now - timedelta(days=20),
                "entry_price": Decimal("450.0000"),
                "exit_date": now - timedelta(days=5),
                "exit_price": Decimal("480.0000"),
                "position_size": Decimal("20.0000"),
                "status": "Closed",
                "pnl": Decimal("600.0000"),
                "pnl_percent": Decimal("6.6667"),
                "thesis": "Data center demand surge",
            },
            {
                "ticker": "TSLA",
                "direction": "Short",
                "entry_date": now - timedelta(days=15),
                "entry_price": Decimal("250.0000"),
                "exit_date": now - timedelta(days=8),
                "exit_price": Decimal("260.0000"),
                "position_size": Decimal("30.0000"),
                "status": "Closed",
                "pnl": Decimal("-300.0000"),
                "pnl_percent": Decimal("-4.0000"),
                "thesis": "Overvalued after rally",
                "emotional_state": "Frustrated",
                "notes": "Should have set tighter stop loss",
            },
            {
                "ticker": "MSFT",
                "direction": "Long",
                "entry_date": now - timedelta(days=3),
                "entry_price": Decimal("415.0000"),
                "position_size": Decimal("25.0000"),
                "stop_loss": Decimal("405.0000"),
                "take_profit": Decimal("435.0000"),
                "status": "Open",
                "thesis": "Cloud growth acceleration",
            },
        ]

        for i, data in enumerate(sample_trades):
            trade = Trade(
                id=uuid.uuid4(),
                user_id=TEST_USER_ID,
                created_at=data["entry_date"],
                updated_at=now,
                **data,
            )
            db.add(trade)
            await db.flush()

            # Tag first two trades with strategies
            if i < len(strategies):
                db.add(
                    TradeStrategyTag(
                        trade_id=trade.id,
                        strategy_id=strategies[i % len(strategies)].id,
                        source="user",
                    )
                )

        await db.commit()
        print("Seeded: 1 user, 3 strategies, 4 trades")


if __name__ == "__main__":
    asyncio.run(seed())
