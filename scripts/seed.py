"""Seed script: creates a test user and comprehensive sample data for all tables."""

import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

# Adjust path so we can import app modules
import sys

sys.path.insert(0, "backend")

from app.db.database import async_session, engine  # noqa: E402
from app.db.models import (  # noqa: E402
    AgentConfig,
    Base,
    Conversation,
    Strategy,
    Trade,
    TradeScreenshot,
    TradeStrategyTag,
    User,
    UserProfile,
)

TEST_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEST_USER_ID_STR = str(TEST_USER_ID)


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.id == TEST_USER_ID))
        if result.scalar_one_or_none():
            print("Test user already exists, skipping seed.")
            return

        now = datetime.utcnow()

        # ── User ──────────────────────────────────────────────────────
        user = User(
            id=TEST_USER_ID,
            azure_ad_b2c_id="dev-test-user-001",
            email="dev@meridian.local",
            display_name="Dev User",
            subscription_tier="Premium",
            created_at=now,
            updated_at=now,
        )
        db.add(user)

        # ── Strategies ────────────────────────────────────────────────
        strategy_defs = [
            ("Breakout", "Price breaks above resistance with volume confirmation"),
            ("Mean Reversion", "Buy oversold conditions, sell overbought via RSI/Bollinger"),
            ("Momentum", "Follow strong trend direction with moving average confirmation"),
            ("Gap Fill", "Trade the fill of overnight gaps on high-volume names"),
            ("VWAP Reclaim", "Enter when price reclaims VWAP with increasing volume"),
        ]
        strategies = []
        for name, desc in strategy_defs:
            s = Strategy(
                id=uuid.uuid4(),
                user_id=TEST_USER_ID,
                name=name,
                description=desc,
                source="user",
                created_at=now - timedelta(days=60),
            )
            strategies.append(s)
            db.add(s)

        await db.flush()

        # ── Trades ────────────────────────────────────────────────────
        # Covers: Open, Closed (win/loss), Cancelled, Long/Short, varied P&L
        sample_trades = [
            # --- Open trades ---
            {
                "ticker": "AAPL",
                "direction": "Long",
                "entry_date": now - timedelta(days=10),
                "entry_price": Decimal("185.5000"),
                "position_size": Decimal("50.0000"),
                "stop_loss": Decimal("180.0000"),
                "take_profit": Decimal("195.0000"),
                "status": "Open",
                "entry_thesis": "Strong earnings beat, AI momentum continuing",
                "market_sentiment": 4,
                "emotional_state": "Confident",
                "market_conditions": "Bullish tech sector, broad market uptrend",
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
                "entry_thesis": "Cloud growth acceleration, Copilot revenue ramp",
                "market_sentiment": 3,
            },
            {
                "ticker": "META",
                "direction": "Short",
                "entry_date": now - timedelta(days=1),
                "entry_price": Decimal("520.0000"),
                "position_size": Decimal("15.0000"),
                "stop_loss": Decimal("535.0000"),
                "take_profit": Decimal("490.0000"),
                "status": "Open",
                "entry_thesis": "Overextended after earnings pop, expecting mean reversion",
                "market_sentiment": 2,
                "emotional_state": "Cautious",
            },
            # --- Closed trades (winners) ---
            {
                "ticker": "NVDA",
                "direction": "Long",
                "entry_date": now - timedelta(days=30),
                "entry_price": Decimal("450.0000"),
                "exit_date": now - timedelta(days=20),
                "exit_price": Decimal("480.0000"),
                "position_size": Decimal("20.0000"),
                "status": "Closed",
                "pnl": Decimal("600.0000"),
                "pnl_percent": Decimal("6.6667"),
                "entry_thesis": "Data center demand surge, GTC catalyst",
                "exit_thesis": "Hit take-profit target, momentum fading",
                "market_sentiment": 4,
                "emotional_state": "Confident",
                "market_conditions": "AI sector euphoria",
            },
            {
                "ticker": "AMZN",
                "direction": "Long",
                "entry_date": now - timedelta(days=25),
                "entry_price": Decimal("178.0000"),
                "exit_date": now - timedelta(days=15),
                "exit_price": Decimal("192.0000"),
                "position_size": Decimal("40.0000"),
                "status": "Closed",
                "pnl": Decimal("560.0000"),
                "pnl_percent": Decimal("7.8652"),
                "entry_thesis": "AWS re-acceleration, Prime Day catalyst ahead",
                "exit_thesis": "Took profits ahead of FOMC uncertainty",
                "market_sentiment": 3,
                "emotional_state": "Calm",
            },
            {
                "ticker": "SPY",
                "direction": "Short",
                "entry_date": now - timedelta(days=18),
                "entry_price": Decimal("525.0000"),
                "exit_date": now - timedelta(days=14),
                "exit_price": Decimal("515.0000"),
                "position_size": Decimal("100.0000"),
                "status": "Closed",
                "pnl": Decimal("1000.0000"),
                "pnl_percent": Decimal("1.9048"),
                "entry_thesis": "Overbought RSI, FOMC risk, VIX rising",
                "exit_thesis": "Covered at support, thesis played out",
                "market_sentiment": 2,
                "emotional_state": "Focused",
                "market_conditions": "Pre-FOMC volatility spike",
            },
            # --- Closed trades (losers) ---
            {
                "ticker": "TSLA",
                "direction": "Short",
                "entry_date": now - timedelta(days=22),
                "entry_price": Decimal("250.0000"),
                "exit_date": now - timedelta(days=16),
                "exit_price": Decimal("260.0000"),
                "position_size": Decimal("30.0000"),
                "status": "Closed",
                "pnl": Decimal("-300.0000"),
                "pnl_percent": Decimal("-4.0000"),
                "entry_thesis": "Overvalued after rally, delivery miss expected",
                "exit_thesis": "Stopped out, thesis invalidated by Musk tweet",
                "market_sentiment": 2,
                "emotional_state": "Frustrated",
                "notes": "Should have set tighter stop loss. Lesson: don't fight momentum.",
            },
            {
                "ticker": "AMD",
                "direction": "Long",
                "entry_date": now - timedelta(days=12),
                "entry_price": Decimal("165.0000"),
                "exit_date": now - timedelta(days=7),
                "exit_price": Decimal("155.0000"),
                "position_size": Decimal("35.0000"),
                "status": "Closed",
                "pnl": Decimal("-350.0000"),
                "pnl_percent": Decimal("-6.0606"),
                "entry_thesis": "AI chip demand, catching up to NVDA",
                "exit_thesis": "Sector rotation out of semis, cut losses",
                "market_sentiment": 3,
                "emotional_state": "Disappointed",
                "market_conditions": "Sector rotation into defensives",
                "notes": "Position sized too large relative to conviction level.",
            },
            {
                "ticker": "GOOG",
                "direction": "Long",
                "entry_date": now - timedelta(days=40),
                "entry_price": Decimal("155.0000"),
                "exit_date": now - timedelta(days=35),
                "exit_price": Decimal("148.0000"),
                "position_size": Decimal("45.0000"),
                "status": "Closed",
                "pnl": Decimal("-315.0000"),
                "pnl_percent": Decimal("-4.5161"),
                "entry_thesis": "Gemini launch catalyst, search moat",
                "exit_thesis": "Market didn't react to Gemini, cut for better setups",
                "market_sentiment": 3,
                "emotional_state": "Neutral",
            },
            # --- Cancelled trades ---
            {
                "ticker": "COIN",
                "direction": "Long",
                "entry_date": now - timedelta(days=5),
                "entry_price": Decimal("225.0000"),
                "position_size": Decimal("20.0000"),
                "stop_loss": Decimal("210.0000"),
                "take_profit": Decimal("250.0000"),
                "status": "Cancelled",
                "entry_thesis": "Bitcoin breakout, crypto exchange volume spike",
                "notes": "Cancelled — SEC headline risk emerged before fill",
            },
            {
                "ticker": "PLTR",
                "direction": "Long",
                "entry_date": now - timedelta(days=8),
                "entry_price": Decimal("22.5000"),
                "position_size": Decimal("200.0000"),
                "status": "Cancelled",
                "entry_thesis": "Government contract pipeline, AI platform traction",
                "notes": "Cancelled — spreads too wide at open, re-evaluate later",
            },
        ]

        trade_ids = []
        for data in sample_trades:
            trade = Trade(
                id=uuid.uuid4(),
                user_id=TEST_USER_ID,
                created_at=data["entry_date"],
                updated_at=now,
                **data,
            )
            db.add(trade)
            await db.flush()
            trade_ids.append((trade.id, data["ticker"], data["status"]))

        # ── Trade-Strategy Tags ───────────────────────────────────────
        # Tag trades with strategies (multiple tags per trade, mixed sources)
        tag_map = [
            (0, 0, "user"),   # AAPL → Breakout
            (0, 2, "agent"),  # AAPL → Momentum (agent-suggested)
            (1, 2, "user"),   # MSFT → Momentum
            (2, 1, "user"),   # META → Mean Reversion
            (3, 2, "user"),   # NVDA → Momentum
            (3, 0, "user"),   # NVDA → Breakout
            (4, 3, "user"),   # AMZN → Gap Fill
            (5, 1, "agent"),  # SPY → Mean Reversion
            (6, 2, "user"),   # TSLA → Momentum
            (7, 0, "user"),   # AMD → Breakout
            (7, 4, "agent"),  # AMD → VWAP Reclaim
            (8, 2, "user"),   # GOOG → Momentum
            (9, 0, "user"),   # COIN → Breakout
        ]
        for trade_idx, strat_idx, source in tag_map:
            db.add(
                TradeStrategyTag(
                    trade_id=trade_ids[trade_idx][0],
                    strategy_id=strategies[strat_idx].id,
                    source=source,
                )
            )

        # ── Trade Screenshots ─────────────────────────────────────────
        screenshot_data = [
            (0, "https://charts.example.com/aapl-daily-breakout.png", "AAPL daily chart — breakout above resistance"),
            (0, "https://charts.example.com/aapl-15m-entry.png", "AAPL 15m entry timing"),
            (3, "https://charts.example.com/nvda-entry-setup.png", "NVDA entry setup — volume surge"),
            (3, "https://charts.example.com/nvda-exit-target.png", "NVDA exit at take-profit level"),
            (5, "https://charts.example.com/spy-rsi-overbought.png", "SPY RSI divergence at resistance"),
            (6, "https://charts.example.com/tsla-stopped-out.png", "TSLA stop-loss hit — gap up against short"),
        ]
        for trade_idx, url, caption in screenshot_data:
            db.add(
                TradeScreenshot(
                    id=uuid.uuid4(),
                    trade_id=trade_ids[trade_idx][0],
                    blob_url=url,
                    caption=caption,
                    uploaded_at=now - timedelta(days=trade_idx, hours=2),
                )
            )

        # ── Conversations ─────────────────────────────────────────────
        conversations = [
            {
                "agent_type": "screener",
                "title": "Morning scan — tech breakouts",
                "messages": [
                    {"role": "user", "content": "Show me tech stocks breaking out above resistance today"},
                    {
                        "role": "assistant",
                        "content": "I found 3 stocks showing breakout patterns:\n\n1. **AAPL** — Breaking above $185 resistance with 1.5x avg volume\n2. **CRM** — Clearing $310 with RSI expansion\n3. **NOW** — New 52-week high on strong cloud earnings\n\nWould you like me to pull up detailed charts for any of these?",
                    },
                    {"role": "user", "content": "Tell me more about AAPL"},
                    {
                        "role": "assistant",
                        "content": "AAPL is trading at $186.20, up 1.8% today. Key levels:\n- **Support:** $183.50 (previous resistance, now support)\n- **Resistance:** $190 (next target)\n- **Volume:** 1.5x 20-day average\n- **RSI:** 62 — room to run before overbought\n\nThe breakout looks clean with earnings momentum behind it.",
                    },
                ],
                "created_at": now - timedelta(days=10, hours=6),
            },
            {
                "agent_type": "analyst",
                "title": "NVDA position review",
                "messages": [
                    {"role": "user", "content": "How's my NVDA position looking? Should I take profits?"},
                    {
                        "role": "assistant",
                        "content": "Your NVDA long from $450 is up 6.7% at $480. Here's my analysis:\n\n**Bull case:** Data center revenue beat, GTC announcements next week\n**Bear case:** RSI at 71 (approaching overbought), sector showing fatigue\n\n**Recommendation:** Consider taking partial profits (50%) here and trailing the rest with a stop at $465. You've hit your take-profit zone and locking in gains reduces risk into GTC.",
                    },
                    {"role": "user", "content": "Good call, I'll close the full position at $480"},
                ],
                "created_at": now - timedelta(days=20, hours=3),
            },
            {
                "agent_type": "coach",
                "title": "Weekly performance review",
                "messages": [
                    {"role": "user", "content": "Review my trading this week"},
                    {
                        "role": "assistant",
                        "content": "Here's your weekly performance summary:\n\n**Stats:** 3 trades closed, 2 winners (67% win rate), +$960 net P&L\n\n**Strengths:**\n- Good risk management on NVDA — took profits at target\n- SPY short was well-timed with your macro thesis\n\n**Areas to improve:**\n- TSLA short: position size was too large for a counter-trend trade. Consider sizing down when trading against momentum.\n- Emotional note: I noticed frustration after the TSLA loss. Take a break after stop-outs before entering new trades.\n\n**Action items:**\n1. Review your position sizing rules for counter-trend setups\n2. Add a 30-minute cooldown rule after losses",
                    },
                ],
                "created_at": now - timedelta(days=7, hours=1),
            },
        ]
        for conv in conversations:
            db.add(
                Conversation(
                    id=str(uuid.uuid4()),
                    user_id=TEST_USER_ID_STR,
                    agent_type=conv["agent_type"],
                    title=conv["title"],
                    messages=conv["messages"],
                    created_at=conv["created_at"],
                    updated_at=now,
                )
            )

        # ── Agent Configs ─────────────────────────────────────────────
        agent_configs = [
            {
                "agent_type": "screener",
                "custom_system_prompt": "Focus on US large-cap tech and semiconductor stocks. Prefer breakout and momentum setups.",
                "settings": {
                    "default_market": "US",
                    "sectors": ["Technology", "Semiconductors"],
                    "min_volume": 1000000,
                    "min_market_cap_b": 10,
                },
                "is_enabled": True,
            },
            {
                "agent_type": "analyst",
                "custom_system_prompt": None,
                "settings": {"alert_on_stop_proximity": True, "pnl_update_interval_min": 15},
                "is_enabled": True,
            },
            {
                "agent_type": "coach",
                "custom_system_prompt": "Be direct and data-driven. Don't sugarcoat feedback.",
                "settings": {"review_frequency": "weekly", "include_emotional_analysis": True},
                "is_enabled": True,
            },
        ]
        for cfg in agent_configs:
            db.add(
                AgentConfig(
                    id=str(uuid.uuid4()),
                    user_id=TEST_USER_ID_STR,
                    agent_type=cfg["agent_type"],
                    custom_system_prompt=cfg["custom_system_prompt"],
                    settings=cfg["settings"],
                    is_enabled=cfg["is_enabled"],
                    created_at=now - timedelta(days=30),
                    updated_at=now,
                )
            )

        # ── User Profile ─────────────────────────────────────────────
        db.add(
            UserProfile(
                id=str(uuid.uuid4()),
                user_id=TEST_USER_ID_STR,
                trading_style="Swing",
                preferred_sectors=["Technology", "Semiconductors", "Consumer Discretionary"],
                watchlist_tickers=["AAPL", "NVDA", "MSFT", "AMZN", "TSLA", "META", "GOOG", "AMD"],
                risk_profile="Moderate",
                strategy_performance={
                    "Breakout": {"win_rate": 0.65, "avg_rr": 2.1, "total_trades": 23},
                    "Mean Reversion": {"win_rate": 0.58, "avg_rr": 1.5, "total_trades": 15},
                    "Momentum": {"win_rate": 0.72, "avg_rr": 2.8, "total_trades": 31},
                    "Gap Fill": {"win_rate": 0.55, "avg_rr": 1.2, "total_trades": 8},
                    "VWAP Reclaim": {"win_rate": 0.60, "avg_rr": 1.8, "total_trades": 5},
                },
                last_refreshed=now - timedelta(hours=6),
            )
        )

        await db.commit()

        # Print summary
        open_count = sum(1 for _, _, s in trade_ids if s == "Open")
        closed_count = sum(1 for _, _, s in trade_ids if s == "Closed")
        cancelled_count = sum(1 for _, _, s in trade_ids if s == "Cancelled")
        print(
            f"Seeded: 1 user, {len(strategies)} strategies, "
            f"{len(trade_ids)} trades ({open_count} open, {closed_count} closed, "
            f"{cancelled_count} cancelled), {len(tag_map)} strategy tags, "
            f"{len(screenshot_data)} screenshots, {len(conversations)} conversations, "
            f"{len(agent_configs)} agent configs, 1 user profile"
        )


if __name__ == "__main__":
    asyncio.run(seed())
