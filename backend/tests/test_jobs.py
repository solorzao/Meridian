"""Tests for background job execute() functions."""

import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Pre-import all job modules so @patch decorator can resolve them
import app.jobs.daily_summary  # noqa: F401
import app.jobs.embedding_job  # noqa: F401
import app.jobs.profile_refresh  # noqa: F401
import app.jobs.screener_job  # noqa: F401


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_async_session_factory(mock_db):
    """Return an async context manager factory that yields mock_db."""
    class _FakeSession:
        async def __aenter__(self):
            return mock_db
        async def __aexit__(self, *args):
            pass
    return _FakeSession


# ── daily_summary tests ─────────────────────────────────────────────────────

class TestDailySummary:

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        # Make add synchronous (it's not an async method on the real session)
        db.add = MagicMock()
        return db

    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        return result

    @pytest.mark.asyncio
    @patch("app.jobs.daily_summary.async_session")
    async def test_no_trades_logs_skip(self, mock_session_factory, mock_db, mock_result):
        """When there are no open trades, the job returns early."""
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        # Should complete without error; no quote calls
        await app.jobs.daily_summary.execute(user_id)

    @pytest.mark.asyncio
    @patch("app.jobs.daily_summary.market_data_service")
    @patch("app.jobs.daily_summary.async_session")
    async def test_fetches_quotes_for_open_trades(self, mock_session_factory, mock_mds, mock_db, mock_result):
        """When open trades exist, get_quote is called for each ticker."""
        trade = MagicMock()
        trade.ticker = "AAPL"
        trade.direction = "Long"
        trade.entry_price = Decimal("150.00")
        trade.position_size = Decimal("100")

        mock_result.scalars.return_value.all.return_value = [trade]
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        quote = MagicMock()
        quote.price = 155.0
        mock_mds.get_quote.return_value = quote

        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        await app.jobs.daily_summary.execute(user_id)

        mock_mds.get_quote.assert_called_once_with("AAPL")


# ── profile_refresh tests ───────────────────────────────────────────────────

class TestProfileRefresh:

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.mark.asyncio
    @patch("app.jobs.profile_refresh.async_session")
    async def test_no_trades_returns_early(self, mock_session_factory, mock_db):
        """When there are no closed trades, the job returns without updating."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        await app.jobs.profile_refresh.execute(user_id, "00000000-0000-0000-0000-000000000001")

        mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.jobs.profile_refresh.async_session")
    async def test_calculates_trading_style_day_trader(self, mock_session_factory, mock_db):
        """If avg hold time < 1 day, trading style should be 'Day Trader'."""
        trade = MagicMock()
        trade.entry_date = datetime(2025, 1, 15, 10, 0)
        trade.exit_date = datetime(2025, 1, 15, 14, 0)  # Same day = ~0.17 days
        trade.pnl = Decimal("50.00")
        trade.strategy_tags = []
        trade.ticker = "AAPL"

        # First execute call returns trades, second returns profile (None = new profile)
        trades_result = MagicMock()
        trades_result.scalars.return_value.all.return_value = [trade]
        profile_result = MagicMock()
        profile_result.scalar_one_or_none.return_value = None

        mock_db.execute = AsyncMock(side_effect=[trades_result, profile_result])
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        await app.jobs.profile_refresh.execute(user_id, "00000000-0000-0000-0000-000000000001")

        # A new profile should be added
        mock_db.add.assert_called_once()
        added_profile = mock_db.add.call_args[0][0]
        assert added_profile.trading_style == "Day Trader"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.jobs.profile_refresh.async_session")
    async def test_creates_profile_when_missing(self, mock_session_factory, mock_db):
        """When no profile exists, a new one is created."""
        trade = MagicMock()
        trade.entry_date = datetime(2025, 1, 1, 10, 0)
        trade.exit_date = datetime(2025, 1, 20, 10, 0)  # 19 days = Position Trader
        trade.pnl = Decimal("200.00")
        trade.strategy_tags = []
        trade.ticker = "MSFT"

        trades_result = MagicMock()
        trades_result.scalars.return_value.all.return_value = [trade]
        profile_result = MagicMock()
        profile_result.scalar_one_or_none.return_value = None

        mock_db.execute = AsyncMock(side_effect=[trades_result, profile_result])
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        await app.jobs.profile_refresh.execute(user_id, "00000000-0000-0000-0000-000000000001")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


# ── screener_job tests ──────────────────────────────────────────────────────

class TestScreenerJob:

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.mark.asyncio
    @patch("app.jobs.screener_job.async_session")
    async def test_returns_early_when_config_missing(self, mock_session_factory, mock_db):
        """When no agent config row exists, the job skips."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        await app.jobs.screener_job.execute("00000000-0000-0000-0000-000000000001")

    @pytest.mark.asyncio
    @patch("app.jobs.screener_job.async_session")
    async def test_returns_early_when_disabled(self, mock_session_factory, mock_db):
        """When the config exists but is_enabled is False, the job skips."""
        config = MagicMock()
        config.is_enabled = False
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = config
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        await app.jobs.screener_job.execute("00000000-0000-0000-0000-000000000001")

    @pytest.mark.asyncio
    @patch("app.jobs.screener_job.screener_service")
    @patch("app.jobs.screener_job.async_session")
    async def test_runs_screener_when_enabled(self, mock_session_factory, mock_screener_svc, mock_db):
        """When config is enabled, screener_service.screen is called."""
        config = MagicMock()
        config.is_enabled = True
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = config
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        screen_result = MagicMock()
        screen_result.matches = []
        mock_screener_svc.screen.return_value = screen_result

        await app.jobs.screener_job.execute("00000000-0000-0000-0000-000000000001")

        mock_screener_svc.screen.assert_called_once()


# ── embedding_job tests ─────────────────────────────────────────────────────

class TestEmbeddingJob:

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        return db

    @pytest.mark.asyncio
    @patch("app.jobs.embedding_job.async_session")
    async def test_returns_early_when_trade_not_found(self, mock_session_factory, mock_db):
        """When the trade is not found, the job returns early."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        trade_id = uuid.uuid4()
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        await app.jobs.embedding_job.execute(trade_id, user_id)

    @pytest.mark.asyncio
    @patch("app.jobs.embedding_job.async_session")
    async def test_builds_text_representation(self, mock_session_factory, mock_db):
        """When trade is found, it builds a text embedding string."""
        trade = MagicMock()
        trade.ticker = "AAPL"
        trade.direction = "Long"
        trade.entry_price = Decimal("150.00")
        trade.entry_date = datetime(2025, 1, 15)
        trade.exit_price = Decimal("160.00")
        trade.exit_date = datetime(2025, 1, 20)
        trade.pnl = Decimal("1000.00")
        trade.thesis = "Breakout play"
        trade.notes = "Clean setup"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = trade
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_session_factory.return_value = _make_async_session_factory(mock_db)()

        trade_id = uuid.uuid4()
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")

        # Should complete without error, building the trade_text string
        await app.jobs.embedding_job.execute(trade_id, user_id)
