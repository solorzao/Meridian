"""Shared test fixtures for the Meridian backend test suite."""

import sys
import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

# Attempt to import heavy third-party modules. Only stub them if they
# are genuinely unavailable (e.g. missing C compiler for numba).
for _mod_name in ("pandas_ta", "yfinance"):
    try:
        __import__(_mod_name)
    except ImportError:
        sys.modules[_mod_name] = MagicMock()

from app.db.models import Conversation, Strategy, Trade, TradeStrategyTag, User


# ── Identity fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def user_id_str() -> str:
    return "00000000-0000-0000-0000-000000000001"


# ── Database mock fixtures ──────────────────────────────────────────────────

@pytest.fixture
def mock_result():
    """Configurable mock for SQLAlchemy result objects.

    Usage in tests:
        mock_result.scalar_one_or_none.return_value = some_value
        mock_result.scalars.return_value.all.return_value = [item1, item2]
        mock_result.all.return_value = [(strategy, 5)]
        mock_result.scalar_one.return_value = 42
        mock_result.one_or_none.return_value = (strategy, 5)
    """
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    result.scalars = MagicMock()
    result.scalars.return_value.all = MagicMock(return_value=[])
    result.all = MagicMock(return_value=[])
    result.scalar_one = MagicMock(return_value=0)
    result.one_or_none = MagicMock(return_value=None)
    return result


@pytest.fixture
def mock_db(mock_result):
    """AsyncMock simulating an AsyncSession with common async methods."""
    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    db.refresh = AsyncMock()
    return db


# ── Sample model fixtures ──────────────────────────────────────────────────

@pytest.fixture
def sample_trade(user_id) -> MagicMock:
    trade = MagicMock(spec=Trade)
    trade.id = uuid.uuid4()
    trade.user_id = user_id
    trade.ticker = "AAPL"
    trade.direction = "Long"
    trade.status = "Open"
    trade.entry_date = datetime(2025, 1, 15, 10, 30)
    trade.entry_price = Decimal("150.00")
    trade.exit_date = None
    trade.exit_price = None
    trade.position_size = Decimal("100")
    trade.stop_loss = Decimal("145.00")
    trade.take_profit = Decimal("165.00")
    trade.pnl = None
    trade.pnl_percent = None
    trade.thesis = "Bullish breakout pattern"
    trade.emotional_state = "Confident"
    trade.market_conditions = "Trending up"
    trade.notes = "Entry after gap up"
    trade.created_at = datetime(2025, 1, 15, 10, 30)
    trade.updated_at = datetime(2025, 1, 15, 10, 30)

    # Strategy tags — default to empty list
    trade.strategy_tags = []

    return trade


@pytest.fixture
def sample_strategy(user_id) -> MagicMock:
    strategy = MagicMock(spec=Strategy)
    strategy.id = uuid.uuid4()
    strategy.user_id = user_id
    strategy.name = "Momentum Breakout"
    strategy.description = "Buy on confirmed breakouts above resistance"
    strategy.source = "user"
    strategy.created_at = datetime(2025, 1, 10, 8, 0)
    return strategy


@pytest.fixture
def sample_user(user_id) -> MagicMock:
    user = MagicMock(spec=User)
    user.id = user_id
    user.azure_ad_b2c_id = "azure-id-abc123"
    user.email = "trader@example.com"
    user.display_name = "Test Trader"
    user.subscription_tier = "Free"
    user.stripe_customer_id = None
    user.created_at = datetime(2025, 1, 1, 0, 0)
    user.updated_at = datetime(2025, 1, 1, 0, 0)
    return user


@pytest.fixture
def sample_conversation(user_id_str) -> MagicMock:
    conversation = MagicMock(spec=Conversation)
    conversation.id = str(uuid.uuid4())
    conversation.user_id = user_id_str
    conversation.agent_type = "screener"
    conversation.title = "Market scan for tech setups"
    conversation.messages = [
        {"role": "user", "content": "Find bullish setups in tech", "timestamp": "2025-01-15T10:00:00"},
        {"role": "assistant", "content": "Found 3 setups.", "timestamp": "2025-01-15T10:00:01"},
    ]
    conversation.created_at = datetime(2025, 1, 15, 10, 0)
    conversation.updated_at = datetime(2025, 1, 15, 10, 0)
    return conversation
