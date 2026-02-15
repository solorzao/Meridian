"""Integration tests for the strategies router (/api/strategies)."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import get_current_user_id
from app.db.database import get_db
from app.models.strategy_schemas import StrategyResponse


# ── Fixtures ─────────────────────────────────────────────────────────────────

USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def _sample_strategy_response(**overrides) -> StrategyResponse:
    defaults = dict(
        id=str(uuid.uuid4()),
        name="Momentum Breakout",
        description="Buy on confirmed breakouts above resistance",
        source="user",
        created_at=datetime(2025, 1, 10, 8, 0),
        trade_count=3,
    )
    defaults.update(overrides)
    return StrategyResponse(**defaults)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def app_with_overrides(mock_db):
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
@patch("app.routers.strategies.strategy_service")
async def test_list_strategies_200(mock_service, client):
    sample = _sample_strategy_response()
    mock_service.get_strategies = AsyncMock(return_value=[sample])

    resp = await client.get("/api/strategies")

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Momentum Breakout"


@pytest.mark.asyncio
@patch("app.routers.strategies.strategy_service")
async def test_get_strategy_200(mock_service, client):
    strategy_id = str(uuid.uuid4())
    sample = _sample_strategy_response(id=strategy_id)
    mock_service.get_strategy = AsyncMock(return_value=sample)

    resp = await client.get(f"/api/strategies/{strategy_id}")

    assert resp.status_code == 200
    assert resp.json()["id"] == strategy_id


@pytest.mark.asyncio
@patch("app.routers.strategies.strategy_service")
async def test_get_strategy_404(mock_service, client):
    mock_service.get_strategy = AsyncMock(return_value=None)

    resp = await client.get(f"/api/strategies/{uuid.uuid4()}")

    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.routers.strategies.strategy_service")
async def test_create_strategy_201(mock_service, client):
    sample = _sample_strategy_response()
    mock_service.create_strategy = AsyncMock(return_value=sample)

    resp = await client.post(
        "/api/strategies",
        json={"name": "Momentum Breakout", "description": "Buy on breakouts"},
    )

    assert resp.status_code == 201
    assert resp.json()["name"] == "Momentum Breakout"


@pytest.mark.asyncio
@patch("app.routers.strategies.strategy_service")
async def test_delete_strategy_204(mock_service, client):
    mock_service.delete_strategy = AsyncMock(return_value=True)

    resp = await client.delete(f"/api/strategies/{uuid.uuid4()}")

    assert resp.status_code == 204


@pytest.mark.asyncio
@patch("app.routers.strategies.strategy_service")
async def test_delete_strategy_404(mock_service, client):
    mock_service.delete_strategy = AsyncMock(return_value=False)

    resp = await client.delete(f"/api/strategies/{uuid.uuid4()}")

    assert resp.status_code == 404
