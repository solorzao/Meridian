"""Integration tests for the analytics router (/api/analytics)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.models.indicator_schemas import IndicatorBar, IndicatorResponse
from app.models.schemas import OHLCVBar, OHLCVResponse, QuoteResponse
from app.models.screener_schemas import ScreenerMatch, ScreenerResponse


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def app_instance():
    """Return the FastAPI app. Analytics routes have no db/auth deps."""
    from app.main import app
    from app.middleware.rate_limiter import limiter

    # Disable rate limiter for testing
    limiter.enabled = False
    yield app
    limiter.enabled = True


@pytest.fixture
async def client(app_instance):
    transport = ASGITransport(app=app_instance, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.routers.analytics.market_data_service")
async def test_get_quote_200(mock_mds, client):
    """GET /api/analytics/quote/AAPL returns the quote."""
    mock_mds.get_quote.return_value = QuoteResponse(
        ticker="AAPL",
        price=175.50,
        change=2.30,
        change_percent=1.33,
        volume=45000000,
        timestamp=datetime(2025, 1, 15, 16, 0),
    )

    resp = await client.get("/api/analytics/quote/AAPL")

    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert data["price"] == 175.50


@pytest.mark.asyncio
@patch("app.routers.analytics.market_data_service")
async def test_get_ohlcv_200(mock_mds, client):
    """GET /api/analytics/ohlcv/AAPL returns OHLCV data."""
    mock_mds.get_ohlcv.return_value = OHLCVResponse(
        ticker="AAPL",
        bars=[
            OHLCVBar(
                date=datetime(2025, 1, 15),
                open=170.0,
                high=176.0,
                low=169.5,
                close=175.5,
                volume=45000000,
            ),
        ],
        period="1y",
        interval="1d",
    )

    resp = await client.get("/api/analytics/ohlcv/AAPL")

    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert len(data["bars"]) == 1


@pytest.mark.asyncio
@patch("app.routers.analytics.indicator_service")
async def test_calculate_indicators_200(mock_ind, client):
    """POST /api/analytics/indicators returns indicator data."""
    mock_ind.calculate.return_value = IndicatorResponse(
        ticker="AAPL",
        bars=[
            IndicatorBar(
                date="2025-01-15",
                open=170.0,
                high=176.0,
                low=169.5,
                close=175.5,
                volume=45000000,
                indicators={"sma_20": 172.3, "rsi_14": 58.5},
            ),
        ],
        indicators_calculated=["sma_20", "rsi_14"],
    )

    resp = await client.post(
        "/api/analytics/indicators",
        json={
            "ticker": "AAPL",
            "period": "1y",
            "interval": "1d",
            "indicators": ["sma_20", "rsi_14"],
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert "sma_20" in data["indicators_calculated"]


@pytest.mark.asyncio
@patch("app.routers.analytics.screener_service")
async def test_run_screener_200(mock_screener, client):
    """POST /api/analytics/screen returns screener results."""
    mock_screener.screen.return_value = ScreenerResponse(
        matches=[
            ScreenerMatch(
                ticker="TSLA",
                name="Tesla Inc",
                price=250.0,
                change_percent=3.5,
                volume=80000000,
                volume_ratio=1.8,
                rsi_14=62.0,
            ),
        ],
        total_scanned=500,
        criteria_summary="RSI < 70, Volume ratio > 1.5",
    )

    resp = await client.post(
        "/api/analytics/screen",
        json={
            "criteria": {"rsi_14": {"min": 30, "max": 70}},
            "universe": "sp500",
            "limit": 20,
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matches"]) == 1
    assert data["matches"][0]["ticker"] == "TSLA"
    assert data["total_scanned"] == 500


@pytest.mark.asyncio
async def test_get_quote_invalid_ticker_400(client):
    """GET /api/analytics/quote/<invalid> returns 400 for bad tickers."""
    resp = await client.get("/api/analytics/quote/INVALID!!!")

    assert resp.status_code == 400
