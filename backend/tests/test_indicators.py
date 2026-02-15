import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.models.schemas import OHLCVBar, OHLCVResponse
from app.services.indicators import IndicatorService

_pandas_ta_mocked = isinstance(sys.modules.get("pandas_ta"), MagicMock)


@pytest.fixture
def service():
    return IndicatorService()


@pytest.fixture
def mock_ohlcv():
    """Create mock OHLCV data with enough bars for indicators."""
    from datetime import datetime, timedelta

    bars = []
    base_date = datetime(2026, 1, 1)
    for i in range(50):
        price = 150 + i * 0.5
        bars.append(
            OHLCVBar(
                date=base_date + timedelta(days=i),
                open=price - 0.5,
                high=price + 1.0,
                low=price - 1.0,
                close=price,
                volume=1000000 + i * 10000,
            )
        )

    return OHLCVResponse(ticker="AAPL", bars=bars, period="3mo", interval="1d")


@patch("app.services.indicators.market_data_service")
def test_calculate_default_indicators(mock_mds, service, mock_ohlcv):
    mock_mds.get_ohlcv.return_value = mock_ohlcv

    result = service.calculate("AAPL", period="1mo")

    assert result.ticker == "AAPL"
    assert len(result.bars) == 50
    assert "sma_20" in result.indicators_calculated
    assert "rsi_14" in result.indicators_calculated


@patch("app.services.indicators.market_data_service")
def test_calculate_specific_indicators(mock_mds, service, mock_ohlcv):
    mock_mds.get_ohlcv.return_value = mock_ohlcv

    if _pandas_ta_mocked:
        # pandas_ta doesn't support Python 3.14, so provide a real SMA
        # implementation to still test the service's processing logic.
        # The Series must use the same DatetimeIndex as the DataFrame
        # (set_index("date") in the service) so pandas aligns correctly.
        dates = pd.to_datetime([bar.date for bar in mock_ohlcv.bars])
        closes = pd.Series([bar.close for bar in mock_ohlcv.bars], index=dates)
        sma_series = closes.rolling(window=20).mean()
        with patch("app.services.indicators.ta") as mock_ta:
            mock_ta.sma.return_value = sma_series
            result = service.calculate("AAPL", indicators=["sma_20"])
    else:
        result = service.calculate("AAPL", indicators=["sma_20"])

    assert "sma_20" in result.indicators_calculated
    # SMA_20 should have values for bars after the 20th
    last_bar = result.bars[-1]
    assert last_bar.indicators.get("sma_20") is not None


@patch("app.services.indicators.market_data_service")
def test_calculate_unknown_indicator(mock_mds, service, mock_ohlcv):
    mock_mds.get_ohlcv.return_value = mock_ohlcv

    result = service.calculate("AAPL", indicators=["nonexistent"])

    assert "nonexistent" not in result.indicators_calculated
    # Bars should still be returned with None values
    assert result.bars[-1].indicators.get("nonexistent") is None


@patch("app.services.indicators.market_data_service")
def test_calculate_uppercases_ticker(mock_mds, service, mock_ohlcv):
    mock_mds.get_ohlcv.return_value = mock_ohlcv

    result = service.calculate("aapl")

    assert result.ticker == "AAPL"
