"""Unit tests for app.services.trade_service."""

import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import Trade, TradeStrategyTag
from app.models.trade_schemas import CreateTradeRequest, TradeResponse, UpdateTradeRequest
from app.services.trade_service import (
    create_trade,
    delete_trade,
    get_trade,
    get_trade_count,
    get_trades,
    update_trade,
)


# ── get_trades ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_trades_returns_mapped_list(mock_db, mock_result, sample_trade, user_id):
    """get_trades should return a list of TradeResponse objects from DB results."""
    mock_result.scalars.return_value.all.return_value = [sample_trade]

    result = await get_trades(mock_db, user_id)

    assert len(result) == 1
    assert isinstance(result[0], TradeResponse)
    assert result[0].ticker == "AAPL"
    assert result[0].direction == "Long"
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_trades_filters_by_status(mock_db, mock_result, user_id):
    """get_trades should apply a status filter when provided."""
    mock_result.scalars.return_value.all.return_value = []

    result = await get_trades(mock_db, user_id, status="Closed")

    assert result == []
    mock_db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_trades_respects_skip_take(mock_db, mock_result, user_id):
    """get_trades should forward skip/take pagination to the query."""
    mock_result.scalars.return_value.all.return_value = []

    await get_trades(mock_db, user_id, skip=10, take=5)

    mock_db.execute.assert_awaited_once()


# ── get_trade ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_trade_returns_response_when_found(mock_db, mock_result, sample_trade, user_id):
    """get_trade should return a TradeResponse when the trade exists."""
    mock_result.scalar_one_or_none.return_value = sample_trade

    result = await get_trade(mock_db, sample_trade.id, user_id)

    assert result is not None
    assert isinstance(result, TradeResponse)
    assert result.ticker == "AAPL"
    assert result.id == str(sample_trade.id)


@pytest.mark.asyncio
async def test_get_trade_returns_none_when_not_found(mock_db, mock_result, user_id):
    """get_trade should return None when the trade does not exist."""
    mock_result.scalar_one_or_none.return_value = None

    result = await get_trade(mock_db, uuid.uuid4(), user_id)

    assert result is None


# ── create_trade ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_create_trade_uppercases_ticker(mock_get_trade, mock_db, user_id):
    """create_trade should uppercase the ticker symbol."""
    expected_response = TradeResponse(
        id=str(uuid.uuid4()),
        ticker="AAPL",
        direction="Long",
        entry_date=datetime(2025, 1, 15),
        entry_price=Decimal("150.00"),
        position_size=Decimal("100"),
        status="Open",
        strategy_tags=[],
        created_at=datetime(2025, 1, 15),
        updated_at=datetime(2025, 1, 15),
    )
    mock_get_trade.return_value = expected_response

    dto = CreateTradeRequest(
        ticker="aapl",  # lowercase on purpose
        direction="Long",
        entry_date=datetime(2025, 1, 15),
        entry_price=Decimal("150.00"),
        position_size=Decimal("100"),
    )

    result = await create_trade(mock_db, user_id, dto)

    # Verify the Trade object was added to db with uppercased ticker
    mock_db.add.assert_called_once()
    added_trade = mock_db.add.call_args[0][0]
    assert added_trade.ticker == "AAPL"
    assert result.ticker == "AAPL"


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_create_trade_sets_status_open(mock_get_trade, mock_db, user_id):
    """create_trade should set the initial status to 'Open'."""
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)

    dto = CreateTradeRequest(
        ticker="MSFT",
        direction="Long",
        entry_date=datetime(2025, 2, 1),
        entry_price=Decimal("400.00"),
        position_size=Decimal("50"),
    )

    await create_trade(mock_db, user_id, dto)

    added_trade = mock_db.add.call_args[0][0]
    assert added_trade.status == "Open"


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_create_trade_appends_strategy_tags(mock_get_trade, mock_db, user_id):
    """create_trade should append TradeStrategyTag entries for provided strategy_ids."""
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)
    strategy_id = str(uuid.uuid4())

    dto = CreateTradeRequest(
        ticker="GOOG",
        direction="Short",
        entry_date=datetime(2025, 3, 1),
        entry_price=Decimal("175.00"),
        position_size=Decimal("200"),
        strategy_ids=[strategy_id],
    )

    await create_trade(mock_db, user_id, dto)

    added_trade = mock_db.add.call_args[0][0]
    assert len(added_trade.strategy_tags) == 1
    assert added_trade.strategy_tags[0].strategy_id == uuid.UUID(strategy_id)
    assert added_trade.strategy_tags[0].source == "user"


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_create_trade_calls_add_and_commit(mock_get_trade, mock_db, user_id):
    """create_trade should call db.add() and db.commit()."""
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)

    dto = CreateTradeRequest(
        ticker="TSLA",
        direction="Long",
        entry_date=datetime(2025, 4, 1),
        entry_price=Decimal("250.00"),
        position_size=Decimal("10"),
    )

    await create_trade(mock_db, user_id, dto)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


# ── update_trade ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_trade_raises_when_not_found(mock_db, mock_result, user_id):
    """update_trade should raise ValueError when the trade is not found."""
    mock_result.scalar_one_or_none.return_value = None
    trade_id = uuid.uuid4()

    dto = UpdateTradeRequest(status="Closed")

    with pytest.raises(ValueError, match=str(trade_id)):
        await update_trade(mock_db, trade_id, user_id, dto)


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_update_trade_updates_provided_fields(mock_get_trade, mock_db, mock_result, sample_trade, user_id):
    """update_trade should only update fields that are explicitly provided."""
    mock_result.scalar_one_or_none.return_value = sample_trade
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)

    dto = UpdateTradeRequest(thesis="Updated thesis", notes="New notes")

    await update_trade(mock_db, sample_trade.id, user_id, dto)

    assert sample_trade.thesis == "Updated thesis"
    assert sample_trade.notes == "New notes"
    mock_db.commit.assert_awaited()


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_update_trade_pnl_long(mock_get_trade, mock_db, mock_result, user_id):
    """update_trade should calculate P&L for a Long trade: (exit - entry) * size * 1."""
    trade = MagicMock(spec=Trade)
    trade.id = uuid.uuid4()
    trade.user_id = user_id
    trade.direction = "Long"
    trade.entry_price = Decimal("100.00")
    trade.position_size = Decimal("10")
    trade.exit_price = None
    trade.status = "Open"
    trade.strategy_tags = []
    mock_result.scalar_one_or_none.return_value = trade
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)

    dto = UpdateTradeRequest(exit_price=Decimal("110.00"), status="Closed")

    await update_trade(mock_db, trade.id, user_id, dto)

    # After update: exit_price=110, status=Closed, direction=Long
    # P&L = (110 - 100) * 10 * 1 = 100
    assert trade.pnl == Decimal("100.00")
    # P&L % = (110 - 100) / 100 * 100 * 1 = 10
    assert trade.pnl_percent == Decimal("10.00")


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_update_trade_pnl_short(mock_get_trade, mock_db, mock_result, user_id):
    """update_trade should calculate P&L for a Short trade: (exit - entry) * size * -1."""
    trade = MagicMock(spec=Trade)
    trade.id = uuid.uuid4()
    trade.user_id = user_id
    trade.direction = "Short"
    trade.entry_price = Decimal("100.00")
    trade.position_size = Decimal("10")
    trade.exit_price = None
    trade.status = "Open"
    trade.strategy_tags = []
    mock_result.scalar_one_or_none.return_value = trade
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)

    dto = UpdateTradeRequest(exit_price=Decimal("90.00"), status="Closed")

    await update_trade(mock_db, trade.id, user_id, dto)

    # P&L = (90 - 100) * 10 * -1 = 100 (profit on short)
    assert trade.pnl == Decimal("100.00")
    # P&L % = (90 - 100) / 100 * 100 * -1 = 10
    assert trade.pnl_percent == Decimal("10.00")


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_update_trade_pnl_zero_entry_price(mock_get_trade, mock_db, mock_result, user_id):
    """update_trade should handle zero entry_price by setting pnl_percent to 0."""
    trade = MagicMock(spec=Trade)
    trade.id = uuid.uuid4()
    trade.user_id = user_id
    trade.direction = "Long"
    trade.entry_price = Decimal("0")
    trade.position_size = Decimal("10")
    trade.exit_price = None
    trade.status = "Open"
    trade.strategy_tags = []
    mock_result.scalar_one_or_none.return_value = trade
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)

    dto = UpdateTradeRequest(exit_price=Decimal("50.00"), status="Closed")

    await update_trade(mock_db, trade.id, user_id, dto)

    # P&L = (50 - 0) * 10 * 1 = 500
    assert trade.pnl == Decimal("500.00")
    # P&L % = 0 when entry_price == 0
    assert trade.pnl_percent == Decimal(0)


@pytest.mark.asyncio
@patch("app.services.trade_service.get_trade")
async def test_update_trade_replaces_strategy_tags(mock_get_trade, mock_db, mock_result, user_id):
    """update_trade should clear and replace strategy_tags when strategy_ids provided."""
    trade = MagicMock(spec=Trade)
    trade.id = uuid.uuid4()
    trade.user_id = user_id
    trade.direction = "Long"
    trade.entry_price = Decimal("100.00")
    trade.position_size = Decimal("10")
    trade.exit_price = None
    trade.status = "Open"
    trade.strategy_tags = [MagicMock(spec=TradeStrategyTag)]
    mock_result.scalar_one_or_none.return_value = trade
    mock_get_trade.return_value = MagicMock(spec=TradeResponse)

    new_strategy_id = str(uuid.uuid4())
    dto = UpdateTradeRequest(strategy_ids=[new_strategy_id])

    await update_trade(mock_db, trade.id, user_id, dto)

    # After update, the old tag should be cleared and one new tag appended
    assert len(trade.strategy_tags) == 1
    new_tag = trade.strategy_tags[0]
    assert isinstance(new_tag, TradeStrategyTag)
    assert str(new_tag.strategy_id) == new_strategy_id


# ── delete_trade ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_trade_returns_true_when_found(mock_db, mock_result, sample_trade, user_id):
    """delete_trade should delete and return True when the trade exists."""
    mock_result.scalar_one_or_none.return_value = sample_trade

    result = await delete_trade(mock_db, sample_trade.id, user_id)

    assert result is True
    mock_db.delete.assert_awaited_once_with(sample_trade)
    mock_db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_delete_trade_returns_false_when_not_found(mock_db, mock_result, user_id):
    """delete_trade should return False when the trade does not exist."""
    mock_result.scalar_one_or_none.return_value = None

    result = await delete_trade(mock_db, uuid.uuid4(), user_id)

    assert result is False
    mock_db.delete.assert_not_awaited()


# ── get_trade_count ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_trade_count_returns_correct_count(mock_db, mock_result, user_id):
    """get_trade_count should return the count from the DB."""
    mock_result.scalar_one.return_value = 42

    result = await get_trade_count(mock_db, user_id)

    assert result == 42


@pytest.mark.asyncio
async def test_get_trade_count_filters_by_status(mock_db, mock_result, user_id):
    """get_trade_count should apply a status filter when provided."""
    mock_result.scalar_one.return_value = 7

    result = await get_trade_count(mock_db, user_id, status="Open")

    assert result == 7
    mock_db.execute.assert_awaited_once()
