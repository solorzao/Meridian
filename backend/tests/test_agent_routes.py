"""Integration tests for the agents router (/api/agents)."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import get_current_user_id, get_current_user_id_string
from app.db.database import get_db


# ── Fixtures ─────────────────────────────────────────────────────────────────

USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
USER_ID_STR = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def app_with_overrides(mock_db):
    from app.main import app
    from app.middleware.rate_limiter import limiter

    async def override_get_db():
        yield mock_db

    def override_get_user_id():
        return USER_ID

    def override_get_user_id_string():
        return USER_ID_STR

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_user_id
    app.dependency_overrides[get_current_user_id_string] = override_get_user_id_string

    # Disable rate limiter for testing
    limiter.enabled = False

    yield app

    app.dependency_overrides.clear()
    limiter.enabled = True


@pytest.fixture
async def client(app_with_overrides):
    transport = ASGITransport(app=app_with_overrides, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@patch("app.routers.agents.orchestrator")
async def test_chat_screener_200(mock_orch, client):
    """POST /api/agents/screener/chat with valid request returns 200."""
    mock_orch.chat = AsyncMock(return_value=("Here are 3 setups.", "conv-123"))

    resp = await client.post(
        "/api/agents/screener/chat",
        json={"message": "Find bullish tech setups"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Here are 3 setups."


@pytest.mark.asyncio
async def test_chat_invalid_agent_400(client):
    """POST /api/agents/invalid/chat should return 400."""
    resp = await client.post(
        "/api/agents/invalid/chat",
        json={"message": "hello"},
    )

    assert resp.status_code == 400
    assert "Invalid agent type" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_conversations_200(mock_db, client):
    """GET /api/agents/conversations returns a list."""
    conversation = MagicMock()
    conversation.id = "conv-1"
    conversation.agent_type = "screener"
    conversation.title = "Market scan"
    conversation.messages = [{"role": "user", "content": "hi"}]
    conversation.created_at = datetime(2025, 1, 15, 10, 0)
    conversation.updated_at = datetime(2025, 1, 15, 10, 0)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [conversation]
    mock_db.execute = AsyncMock(return_value=mock_result)

    resp = await client.get("/api/agents/conversations")

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["agentType"] == "screener"
    assert data[0]["messageCount"] == 1


@pytest.mark.asyncio
async def test_get_conversation_200(mock_db, client):
    """GET /api/agents/conversations/{id} returns the conversation when found."""
    conversation = MagicMock()
    conversation.id = "conv-123"
    conversation.user_id = USER_ID_STR
    conversation.agent_type = "analyst"
    conversation.title = "Position review"
    conversation.messages = [{"role": "user", "content": "Check my AAPL"}]
    conversation.created_at = datetime(2025, 1, 15, 10, 0)
    conversation.updated_at = datetime(2025, 1, 15, 10, 0)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = conversation
    mock_db.execute = AsyncMock(return_value=mock_result)

    resp = await client.get("/api/agents/conversations/conv-123")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "conv-123"
    assert data["agentType"] == "analyst"


@pytest.mark.asyncio
async def test_get_conversation_404(mock_db, client):
    """GET /api/agents/conversations/{id} returns 404 when not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    resp = await client.get("/api/agents/conversations/nonexistent")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation_204(mock_db, client):
    """DELETE /api/agents/conversations/{id} returns 204 when found."""
    conversation = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = conversation
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    resp = await client.delete("/api/agents/conversations/conv-123")

    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_conversation_404(mock_db, client):
    """DELETE /api/agents/conversations/{id} returns 404 when not found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=mock_result)

    resp = await client.delete("/api/agents/conversations/nonexistent")

    assert resp.status_code == 404
