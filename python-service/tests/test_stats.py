import math
from datetime import datetime, timedelta

import pytest

from app.models.stats_schemas import TradeInput
from app.services.stats import StatsService


@pytest.fixture
def service():
    return StatsService()


@pytest.fixture
def sample_trades():
    """Create sample trade data."""
    base_date = datetime(2026, 1, 1)
    return [
        TradeInput(
            id="1",
            ticker="AAPL",
            direction="long",
            entry_date=base_date,
            entry_price=150,
            exit_date=base_date + timedelta(days=5),
            exit_price=160,
            position_size=100,
            pnl=1000,
            strategy_tags=["momentum"],
        ),
        TradeInput(
            id="2",
            ticker="MSFT",
            direction="long",
            entry_date=base_date + timedelta(days=7),
            entry_price=300,
            exit_date=base_date + timedelta(days=10),
            exit_price=290,
            position_size=50,
            pnl=-500,
            strategy_tags=["momentum"],
        ),
        TradeInput(
            id="3",
            ticker="GOOGL",
            direction="long",
            entry_date=base_date + timedelta(days=15),
            entry_price=140,
            exit_date=base_date + timedelta(days=20),
            exit_price=155,
            position_size=100,
            pnl=1500,
            strategy_tags=["breakout"],
        ),
        TradeInput(
            id="4",
            ticker="AAPL",
            direction="long",
            entry_date=base_date + timedelta(days=25),
            entry_price=165,
            exit_date=base_date + timedelta(days=28),
            exit_price=170,
            position_size=100,
            pnl=500,
            strategy_tags=["momentum", "breakout"],
        ),
    ]


def test_calculate_overall_stats(service, sample_trades):
    result = service.calculate(sample_trades)

    assert result.overall.total_trades == 4
    assert result.overall.winning_trades == 3
    assert result.overall.losing_trades == 1
    assert result.overall.win_rate == 0.75
    assert result.overall.total_pnl == 2500


def test_calculate_by_strategy(service, sample_trades):
    result = service.calculate(sample_trades)

    strategy_names = [s.strategy_name for s in result.by_strategy]
    assert "momentum" in strategy_names
    assert "breakout" in strategy_names

    momentum = next(s for s in result.by_strategy if s.strategy_name == "momentum")
    assert momentum.total_trades == 3


def test_calculate_by_ticker(service, sample_trades):
    result = service.calculate(sample_trades)

    assert "AAPL" in result.by_ticker
    assert result.by_ticker["AAPL"].total_trades == 2


def test_calculate_monthly_pnl(service, sample_trades):
    result = service.calculate(sample_trades)

    assert "2026-01" in result.monthly_pnl
    assert result.monthly_pnl["2026-01"] == 2500


def test_empty_trades(service):
    result = service.calculate([])

    assert result.overall.total_trades == 0
    assert result.overall.win_rate == 0


def test_profit_factor(service, sample_trades):
    result = service.calculate(sample_trades)

    assert result.overall.profit_factor == 6.0


def test_profit_factor_all_wins(service):
    """When no losses, profit_factor should be infinity."""
    trades = [
        TradeInput(
            id="1",
            ticker="AAPL",
            direction="long",
            entry_date=datetime(2026, 1, 1),
            entry_price=100,
            exit_date=datetime(2026, 1, 5),
            exit_price=110,
            position_size=100,
            pnl=1000,
            strategy_tags=[],
        ),
        TradeInput(
            id="2",
            ticker="MSFT",
            direction="long",
            entry_date=datetime(2026, 1, 6),
            entry_price=200,
            exit_date=datetime(2026, 1, 10),
            exit_price=210,
            position_size=50,
            pnl=500,
            strategy_tags=[],
        ),
    ]

    result = service.calculate(trades)

    assert result.overall.profit_factor == 9999.99


def test_profit_factor_all_losses(service):
    """When no wins, profit_factor should be 0."""
    trades = [
        TradeInput(
            id="1",
            ticker="AAPL",
            direction="long",
            entry_date=datetime(2026, 1, 1),
            entry_price=150,
            exit_date=datetime(2026, 1, 5),
            exit_price=140,
            position_size=100,
            pnl=-1000,
            strategy_tags=[],
        ),
    ]

    result = service.calculate(trades)

    assert result.overall.profit_factor == 0
    assert result.overall.winning_trades == 0


def test_breakeven_trades(service):
    """Breakeven trades (pnl=0) should count as losses."""
    trades = [
        TradeInput(
            id="1",
            ticker="AAPL",
            direction="long",
            entry_date=datetime(2026, 1, 1),
            entry_price=150,
            exit_date=datetime(2026, 1, 5),
            exit_price=150,
            position_size=100,
            pnl=0,
            strategy_tags=[],
        ),
    ]

    result = service.calculate(trades)

    assert result.overall.losing_trades == 1
    assert result.overall.winning_trades == 0


def test_open_trades_excluded(service):
    """Trades without exit_date or pnl should be excluded."""
    trades = [
        TradeInput(
            id="1",
            ticker="AAPL",
            direction="long",
            entry_date=datetime(2026, 1, 1),
            entry_price=150,
            exit_date=None,
            exit_price=None,
            position_size=100,
            pnl=None,
            strategy_tags=[],
        ),
    ]

    result = service.calculate(trades)

    assert result.overall.total_trades == 0


def test_avg_hold_days(service):
    """Average hold days should be correctly calculated."""
    trades = [
        TradeInput(
            id="1",
            ticker="AAPL",
            direction="long",
            entry_date=datetime(2026, 1, 1),
            entry_price=150,
            exit_date=datetime(2026, 1, 11),
            exit_price=160,
            position_size=100,
            pnl=1000,
            strategy_tags=[],
        ),
    ]

    result = service.calculate(trades)

    assert result.overall.avg_hold_days == 10.0


def test_expectancy(service, sample_trades):
    """Expectancy should be calculated correctly."""
    result = service.calculate(sample_trades)

    # win_rate=0.75, avg_win=1000, avg_loss=500
    # expectancy = (0.75 * 1000) - (0.25 * 500) = 750 - 125 = 625
    assert result.overall.expectancy == 625.0
