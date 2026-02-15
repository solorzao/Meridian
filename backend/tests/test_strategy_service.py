"""Unit tests for app.services.strategy_service."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.db.models import Strategy
from app.models.strategy_schemas import CreateStrategyRequest, StrategyResponse
from app.services.strategy_service import (
    create_strategy,
    delete_strategy,
    get_strategies,
    get_strategy,
)


# ── get_strategies ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_strategies_returns_list_with_trade_count(
    mock_db, mock_result, sample_strategy, user_id
):
    """get_strategies should return StrategyResponse list with trade_count from (Strategy, int) tuples."""
    mock_result.all.return_value = [(sample_strategy, 5)]

    result = await get_strategies(mock_db, user_id)

    assert len(result) == 1
    assert isinstance(result[0], StrategyResponse)
    assert result[0].name == "Momentum Breakout"
    assert result[0].trade_count == 5
    assert result[0].source == "user"


@pytest.mark.asyncio
async def test_get_strategies_returns_empty_list(mock_db, mock_result, user_id):
    """get_strategies should return an empty list when no strategies exist."""
    mock_result.all.return_value = []

    result = await get_strategies(mock_db, user_id)

    assert result == []


# ── get_strategy ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_strategy_returns_response_when_found(
    mock_db, mock_result, sample_strategy, user_id
):
    """get_strategy should return a StrategyResponse when the strategy exists."""
    mock_result.one_or_none.return_value = (sample_strategy, 3)

    result = await get_strategy(mock_db, sample_strategy.id, user_id)

    assert result is not None
    assert isinstance(result, StrategyResponse)
    assert result.name == "Momentum Breakout"
    assert result.trade_count == 3


@pytest.mark.asyncio
async def test_get_strategy_returns_none_when_not_found(mock_db, mock_result, user_id):
    """get_strategy should return None when the strategy does not exist."""
    mock_result.one_or_none.return_value = None

    result = await get_strategy(mock_db, uuid.uuid4(), user_id)

    assert result is None


# ── create_strategy ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_strategy_sets_source_user(mock_db, user_id):
    """create_strategy should set source='user' and return response with trade_count=0."""
    dto = CreateStrategyRequest(name="VWAP Bounce", description="Enter at VWAP support")

    result = await create_strategy(mock_db, user_id, dto)

    assert isinstance(result, StrategyResponse)
    assert result.source == "user"
    assert result.trade_count == 0
    assert result.name == "VWAP Bounce"
    assert result.description == "Enter at VWAP support"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_strategy_without_description(mock_db, user_id):
    """create_strategy should work when description is not provided."""
    dto = CreateStrategyRequest(name="Gap Fill")

    result = await create_strategy(mock_db, user_id, dto)

    assert result.name == "Gap Fill"
    assert result.description is None
    assert result.trade_count == 0


# ── delete_strategy ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_strategy_returns_true_when_found(
    mock_db, mock_result, sample_strategy, user_id
):
    """delete_strategy should delete and return True when the strategy exists."""
    mock_result.scalar_one_or_none.return_value = sample_strategy

    result = await delete_strategy(mock_db, sample_strategy.id, user_id)

    assert result is True
    mock_db.delete.assert_awaited_once_with(sample_strategy)
    mock_db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_delete_strategy_returns_false_when_not_found(mock_db, mock_result, user_id):
    """delete_strategy should return False when the strategy does not exist."""
    mock_result.scalar_one_or_none.return_value = None

    result = await delete_strategy(mock_db, uuid.uuid4(), user_id)

    assert result is False
    mock_db.delete.assert_not_awaited()
