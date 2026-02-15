from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.services.market_data import MarketDataService


@pytest.fixture
def service():
    return MarketDataService()


@pytest.fixture
def mock_history():
    """Create mock yfinance history DataFrame."""
    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    data = {
        "Open": [150.0, 151.0, 152.0, 153.0, 154.0],
        "High": [155.0, 156.0, 157.0, 158.0, 159.0],
        "Low": [149.0, 150.0, 151.0, 152.0, 153.0],
        "Close": [152.0, 153.0, 154.0, 155.0, 156.0],
        "Volume": [1000000, 1100000, 1200000, 1300000, 1400000],
    }
    return pd.DataFrame(data, index=dates)


@patch("app.services.market_data.yf.Ticker")
def test_get_ohlcv_returns_bars(mock_ticker_cls, service, mock_history):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = mock_history
    mock_ticker_cls.return_value = mock_ticker

    result = service.get_ohlcv("AAPL", "5d", "1d")

    assert result.ticker == "AAPL"
    assert len(result.bars) == 5
    assert result.bars[0].close == 152.0
    assert result.period == "5d"
    assert result.interval == "1d"


@patch("app.services.market_data.yf.Ticker")
def test_get_ohlcv_empty_raises(mock_ticker_cls, service):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame()
    mock_ticker_cls.return_value = mock_ticker

    with pytest.raises(ValueError, match="No data found"):
        service.get_ohlcv("INVALID")


@patch("app.services.market_data.yf.Ticker")
def test_get_quote(mock_ticker_cls, service):
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 150.0
    mock_ticker.fast_info.previous_close = 148.0
    mock_ticker.fast_info.last_volume = 5000000
    mock_ticker_cls.return_value = mock_ticker

    result = service.get_quote("AAPL")

    assert result.ticker == "AAPL"
    assert result.price == 150.0
    assert result.change == 2.0
    assert result.volume == 5000000


@patch("app.services.market_data.yf.Ticker")
def test_get_ohlcv_uppercases_ticker(mock_ticker_cls, service, mock_history):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = mock_history
    mock_ticker_cls.return_value = mock_ticker

    result = service.get_ohlcv("aapl")

    assert result.ticker == "AAPL"
