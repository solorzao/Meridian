import pytest
from datetime import datetime, timedelta
from app.services.stats import StatsService
from app.models.stats_schemas import TradeInput


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
