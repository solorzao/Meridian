from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Meridian" in response.json()["message"]


@patch("app.services.market_data.yf.Ticker")
def test_market_data_quote(mock_ticker_cls):
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 150.0
    mock_ticker.fast_info.previous_close = 148.0
    mock_ticker.fast_info.last_volume = 5000000
    mock_ticker_cls.return_value = mock_ticker

    response = client.get("/market-data/quote/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["price"] == 150.0


@patch("app.services.market_data.yf.Ticker")
def test_market_data_ohlcv(mock_ticker_cls):
    dates = pd.date_range("2026-01-01", periods=3, freq="D")
    df = pd.DataFrame(
        {
            "Open": [150.0, 151.0, 152.0],
            "High": [155.0, 156.0, 157.0],
            "Low": [149.0, 150.0, 151.0],
            "Close": [152.0, 153.0, 154.0],
            "Volume": [1000000, 1100000, 1200000],
        },
        index=dates,
    )
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = df
    mock_ticker_cls.return_value = mock_ticker

    response = client.get("/market-data/AAPL?period=5d")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert len(data["bars"]) == 3


@patch("app.services.market_data.yf.Ticker")
def test_market_data_ohlcv_not_found(mock_ticker_cls):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame()
    mock_ticker_cls.return_value = mock_ticker

    response = client.get("/market-data/INVALID")
    assert response.status_code == 404


def test_stats_performance():
    trades = [
        {
            "id": "1",
            "ticker": "AAPL",
            "direction": "long",
            "entry_date": "2026-01-01T00:00:00",
            "entry_price": 150,
            "exit_date": "2026-01-10T00:00:00",
            "exit_price": 160,
            "position_size": 100,
            "pnl": 1000,
            "strategy_tags": ["momentum"],
        },
        {
            "id": "2",
            "ticker": "MSFT",
            "direction": "long",
            "entry_date": "2026-01-05T00:00:00",
            "entry_price": 400,
            "exit_date": "2026-01-12T00:00:00",
            "exit_price": 390,
            "position_size": 50,
            "pnl": -500,
            "strategy_tags": ["momentum"],
        },
    ]

    response = client.post("/stats/performance", json=trades)
    assert response.status_code == 200
    data = response.json()
    assert data["overall"]["total_trades"] == 2
    assert data["overall"]["winning_trades"] == 1


def test_stats_performance_empty():
    response = client.post("/stats/performance", json=[])
    assert response.status_code == 200
    data = response.json()
    assert data["overall"]["total_trades"] == 0


@patch("app.services.screener.yf.Ticker")
def test_screener_endpoint(mock_ticker_cls):
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 150.0
    mock_ticker.fast_info.last_volume = 5000000
    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Open": [149.0] * 5,
            "High": [155.0] * 5,
            "Low": [148.0] * 5,
            "Close": [148.0, 148.0, 148.0, 148.0, 150.0],
            "Volume": [5000000] * 5,
        },
        index=dates,
    )
    mock_ticker_cls.return_value = mock_ticker

    response = client.post(
        "/screen",
        json={
            "criteria": {},
            "universe": "custom",
            "custom_tickers": ["AAPL"],
            "limit": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["matches"]) == 1
