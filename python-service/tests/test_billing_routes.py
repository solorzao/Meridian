"""Integration tests for the billing router (/api/billing)."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import get_current_user_id
from app.db.database import get_db


# ── Fixtures ─────────────────────────────────────────────────────────────────

USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


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
@patch("app.routers.billing.billing_service")
async def test_create_checkout_200(mock_service, client):
    """POST /api/billing/checkout returns a checkout URL."""
    mock_service.create_checkout_session = AsyncMock(
        return_value="https://checkout.stripe.com/session/123"
    )

    resp = await client.post(
        "/api/billing/checkout",
        json={
            "successUrl": "https://app.example.com/success",
            "cancelUrl": "https://app.example.com/cancel",
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == "https://checkout.stripe.com/session/123"


@pytest.mark.asyncio
@patch("app.routers.billing.billing_service")
async def test_create_portal_200(mock_service, client):
    """POST /api/billing/portal returns a portal URL."""
    mock_service.create_portal_session = AsyncMock(
        return_value="https://billing.stripe.com/portal/123"
    )

    resp = await client.post(
        "/api/billing/portal",
        json={"returnUrl": "https://app.example.com/settings"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == "https://billing.stripe.com/portal/123"


@pytest.mark.asyncio
@patch("app.routers.billing.billing_service")
async def test_create_portal_400_no_stripe_customer(mock_service, client):
    """POST /api/billing/portal returns 400 when service raises ValueError."""
    mock_service.create_portal_session = AsyncMock(
        side_effect=ValueError("No Stripe customer found")
    )

    resp = await client.post(
        "/api/billing/portal",
        json={"returnUrl": "https://app.example.com/settings"},
    )

    # ValueError is caught by global exception handler -> 400
    # But the router does not catch it explicitly, so the global handler fires
    assert resp.status_code == 400


@pytest.mark.asyncio
@patch("app.routers.billing.billing_service")
async def test_webhook_200(mock_service, mock_db, client):
    """POST /api/billing/webhook with valid signature returns 200."""
    mock_service.handle_webhook = AsyncMock(return_value=None)

    resp = await client.post(
        "/api/billing/webhook",
        content=b'{"type": "checkout.session.completed"}',
        headers={
            "Stripe-Signature": "t=123,v1=abc",
            "Content-Type": "application/json",
        },
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_webhook_400_missing_signature(client):
    """POST /api/billing/webhook without Stripe-Signature returns 400."""
    resp = await client.post(
        "/api/billing/webhook",
        content=b'{"type": "event"}',
        headers={"Content-Type": "application/json"},
    )

    assert resp.status_code == 400
    assert "Missing Stripe-Signature" in resp.json()["detail"]
