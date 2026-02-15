from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.models.screener_schemas import RangeCriteria, ScreenerCriteria
from app.services.screener import ScreenerService


@pytest.fixture
def service():
    return ScreenerService()


def create_mock_ticker(price=150.0, prev_close=148.0, volume=5000000, open_price=149.0):
    """Create a mock yfinance Ticker."""
    mock = MagicMock()
    mock.fast_info.last_price = price
    mock.fast_info.last_volume = volume

    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    data = {
        "Open": [open_price] * 5,
        "High": [price + 5] * 5,
        "Low": [price - 5] * 5,
        "Close": [prev_close, prev_close, prev_close, prev_close, price],
        "Volume": [volume] * 5,
    }
    mock.history.return_value = pd.DataFrame(data, index=dates)
    return mock


@patch("app.services.screener.yf.Ticker")
def test_screen_returns_matches(mock_ticker_cls, service):
    mock_ticker_cls.return_value = create_mock_ticker()
    criteria = ScreenerCriteria()

    result = service.screen(criteria, universe="custom", custom_tickers=["AAPL"], limit=10)

    assert len(result.matches) == 1
    assert result.matches[0].ticker == "AAPL"
    assert result.total_scanned == 1


@patch("app.services.screener.yf.Ticker")
def test_screen_price_filter_excludes(mock_ticker_cls, service):
    mock_ticker_cls.return_value = create_mock_ticker(price=50.0)
    criteria = ScreenerCriteria(price=RangeCriteria(min=100.0))

    result = service.screen(criteria, universe="custom", custom_tickers=["CHEAP"], limit=10)

    assert len(result.matches) == 0


@patch("app.services.screener.yf.Ticker")
def test_screen_volume_ratio_filter(mock_ticker_cls, service):
    mock_ticker_cls.return_value = create_mock_ticker(volume=100)
    criteria = ScreenerCriteria(volume_ratio=RangeCriteria(min=5.0))

    result = service.screen(criteria, universe="custom", custom_tickers=["LOW_VOL"], limit=10)

    # Volume ratio will be 100/100 = 1.0, which is < 5.0
    assert len(result.matches) == 0


@patch("app.services.screener.yf.Ticker")
def test_screen_respects_limit(mock_ticker_cls, service):
    mock_ticker_cls.return_value = create_mock_ticker()
    criteria = ScreenerCriteria()

    result = service.screen(
        criteria, universe="custom",
        custom_tickers=["A", "B", "C", "D", "E"],
        limit=2,
    )

    assert len(result.matches) <= 2


@patch("app.services.screener.yf.Ticker")
def test_screen_handles_errors_gracefully(mock_ticker_cls, service):
    mock_ticker_cls.side_effect = Exception("Network error")
    criteria = ScreenerCriteria()

    result = service.screen(criteria, universe="custom", custom_tickers=["FAIL"], limit=10)

    assert len(result.matches) == 0


def test_summarize_criteria(service):
    criteria = ScreenerCriteria(
        price=RangeCriteria(min=10, max=100),
        gap_percent=RangeCriteria(min=2),
    )
    summary = service._summarize_criteria(criteria)

    assert "price" in summary
    assert "gap" in summary


def test_summarize_no_criteria(service):
    criteria = ScreenerCriteria()
    summary = service._summarize_criteria(criteria)

    assert summary == "No specific criteria"
