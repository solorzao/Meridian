"""Integration tests for the trades router (/api/trades)."""

import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import get_current_user_id
from app.db.database import get_db
from app.models.trade_schemas import TradeResponse


# ── Fixtures ─────────────────────────────────────────────────────────────────

USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def _sample_trade_response(**overrides) -> TradeResponse:
    defaults = dict(
        id=str(uuid.uuid4()),
        ticker="AAPL",
        direction="Long",
        entry_date=datetime(2025, 1, 15, 10, 30),
        entry_price=Decimal("150.00"),
        exit_date=None,
        exit_price=None,
        position_size=Decimal("100"),
        stop_loss=Decimal("145.00"),
        take_profit=Decimal("165.00"),
        pnl=None,
        pnl_percent=None,
        status="Open",
        thesis="Bullish breakout",
        emotional_state="Confident",
        market_conditions="Trending up",
        notes="Entry after gap up",
        strategy_tags=["Momentum Breakout"],
        created_at=datetime(2025, 1, 15, 10, 30),
        updated_at=datetime(2025, 1, 15, 10, 30),
    )
    defaults.update(overrides)
    return TradeResponse(**defaults)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def app_with_overrides(mock_db):
    """Return the FastAPI app with db and auth dependencies overridden."""
    from app.main import app

    async def override_get_db():
        yield mock_db

    def override_get_user_id():
        return USER_ID

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_user_id
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client(app_with_overrides):
    transport = ASGITransport(app=app_with_overrides, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_list_trades_200(mock_service, client):
    sample = _sample_trade_response()
    mock_service.get_trades = AsyncMock(return_value=[sample])

    resp = await client.get("/api/trades")

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["ticker"] == "AAPL"


@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_get_trade_200(mock_service, client):
    trade_id = str(uuid.uuid4())
    sample = _sample_trade_response(id=trade_id)
    mock_service.get_trade = AsyncMock(return_value=sample)

    resp = await client.get(f"/api/trades/{trade_id}")

    assert resp.status_code == 200
    assert resp.json()["id"] == trade_id


@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_get_trade_404(mock_service, client):
    mock_service.get_trade = AsyncMock(return_value=None)

    resp = await client.get(f"/api/trades/{uuid.uuid4()}")

    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_create_trade_201(mock_service, client):
    sample = _sample_trade_response()
    mock_service.create_trade = AsyncMock(return_value=sample)

    resp = await client.post(
        "/api/trades",
        json={
            "ticker": "AAPL",
            "direction": "Long",
            "entryDate": "2025-01-15T10:30:00",
            "entryPrice": "150.00",
            "positionSize": "100",
        },
    )

    assert resp.status_code == 201
    assert resp.json()["ticker"] == "AAPL"


@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_update_trade_200(mock_service, client):
    trade_id = str(uuid.uuid4())
    sample = _sample_trade_response(id=trade_id, status="Closed")
    mock_service.update_trade = AsyncMock(return_value=sample)

    resp = await client.put(
        f"/api/trades/{trade_id}",
        json={"status": "Closed"},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "Closed"


@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_update_trade_404(mock_service, client):
    mock_service.update_trade = AsyncMock(side_effect=ValueError("Trade not found"))

    resp = await client.put(
        f"/api/trades/{uuid.uuid4()}",
        json={"status": "Closed"},
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_delete_trade_204(mock_service, client):
    mock_service.delete_trade = AsyncMock(return_value=True)

    resp = await client.delete(f"/api/trades/{uuid.uuid4()}")

    assert resp.status_code == 204


@pytest.mark.asyncio
@patch("app.routers.trades.trade_service")
async def test_delete_trade_404(mock_service, client):
    mock_service.delete_trade = AsyncMock(return_value=False)

    resp = await client.delete(f"/api/trades/{uuid.uuid4()}")

    assert resp.status_code == 404
