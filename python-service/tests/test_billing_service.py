"""Unit tests for app.services.billing_service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.billing_service import (
    create_checkout_session,
    create_portal_session,
    handle_webhook,
)


# ── create_checkout_session ─────────────────────────────────────────────────


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_create_checkout_user_not_found_raises(mock_stripe, mock_settings, mock_db, mock_result, user_id):
    """create_checkout_session should raise ValueError when the user is not found."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    mock_result.scalar_one_or_none.return_value = None

    with pytest.raises(ValueError, match="User not found"):
        await create_checkout_session(mock_db, user_id, "https://ok", "https://cancel")


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_create_checkout_creates_stripe_customer_when_none(
    mock_stripe, mock_settings, mock_db, mock_result, sample_user, user_id
):
    """create_checkout_session should create a Stripe customer when user has no stripe_customer_id."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    mock_settings.stripe_premium_price_id = "price_123"
    sample_user.stripe_customer_id = None
    mock_result.scalar_one_or_none.return_value = sample_user

    mock_stripe.Customer.create.return_value = MagicMock(id="cus_new_123")
    mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/session")

    result = await create_checkout_session(mock_db, user_id, "https://ok", "https://cancel")

    mock_stripe.Customer.create.assert_called_once_with(
        email=sample_user.email,
        metadata={"meridian_user_id": str(user_id)},
    )
    assert sample_user.stripe_customer_id == "cus_new_123"
    mock_db.commit.assert_awaited()
    assert result == "https://checkout.stripe.com/session"


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_create_checkout_uses_existing_customer(
    mock_stripe, mock_settings, mock_db, mock_result, sample_user, user_id
):
    """create_checkout_session should use the existing stripe_customer_id."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    mock_settings.stripe_premium_price_id = "price_123"
    sample_user.stripe_customer_id = "cus_existing_456"
    mock_result.scalar_one_or_none.return_value = sample_user

    mock_stripe.checkout.Session.create.return_value = MagicMock(url="https://checkout.stripe.com/existing")

    result = await create_checkout_session(mock_db, user_id, "https://ok", "https://cancel")

    mock_stripe.Customer.create.assert_not_called()
    mock_stripe.checkout.Session.create.assert_called_once()
    call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
    assert call_kwargs["customer"] == "cus_existing_456"
    assert result == "https://checkout.stripe.com/existing"


# ── create_portal_session ──────────────────────────────────────────────────


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_create_portal_user_not_found_raises(mock_stripe, mock_settings, mock_db, mock_result, user_id):
    """create_portal_session should raise ValueError when the user is not found."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    mock_result.scalar_one_or_none.return_value = None

    with pytest.raises(ValueError, match="User not found"):
        await create_portal_session(mock_db, user_id, "https://return")


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_create_portal_no_stripe_customer_raises(
    mock_stripe, mock_settings, mock_db, mock_result, sample_user, user_id
):
    """create_portal_session should raise ValueError when user has no stripe_customer_id."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    sample_user.stripe_customer_id = None
    mock_result.scalar_one_or_none.return_value = sample_user

    with pytest.raises(ValueError, match="No Stripe customer found"):
        await create_portal_session(mock_db, user_id, "https://return")


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_create_portal_returns_url(
    mock_stripe, mock_settings, mock_db, mock_result, sample_user, user_id
):
    """create_portal_session should return the portal session URL."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    sample_user.stripe_customer_id = "cus_456"
    mock_result.scalar_one_or_none.return_value = sample_user

    mock_stripe.billing_portal.Session.create.return_value = MagicMock(url="https://billing.stripe.com/portal")

    result = await create_portal_session(mock_db, user_id, "https://return")

    assert result == "https://billing.stripe.com/portal"
    mock_stripe.billing_portal.Session.create.assert_called_once_with(
        customer="cus_456",
        return_url="https://return",
    )


# ── handle_webhook ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_handle_webhook_checkout_completed_upgrades_to_premium(
    mock_stripe, mock_settings, mock_db, mock_result, sample_user
):
    """handle_webhook should upgrade user to Premium on checkout.session.completed."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    mock_settings.stripe_webhook_secret = "whsec_test"

    user_id_str = str(sample_user.id)

    # Build the event mock
    event = MagicMock()
    event.type = "checkout.session.completed"
    event.data.object = {"customer": "cus_789"}
    mock_stripe.Webhook.construct_event.return_value = event

    # Customer.retrieve returns metadata with user ID
    customer_mock = MagicMock()
    customer_mock.metadata.get.return_value = user_id_str
    mock_stripe.Customer.retrieve.return_value = customer_mock

    # DB returns the user
    sample_user.subscription_tier = "Free"
    mock_result.scalar_one_or_none.return_value = sample_user

    await handle_webhook(mock_db, "payload_body", "sig_header")

    assert sample_user.subscription_tier == "Premium"
    mock_db.commit.assert_awaited()


@pytest.mark.asyncio
@patch("app.services.billing_service.settings")
@patch("app.services.billing_service.stripe")
async def test_handle_webhook_subscription_deleted_downgrades_to_free(
    mock_stripe, mock_settings, mock_db, mock_result, sample_user
):
    """handle_webhook should downgrade user to Free on customer.subscription.deleted."""
    mock_settings.stripe_secret_key = "sk_test_xxx"
    mock_settings.stripe_webhook_secret = "whsec_test"

    user_id_str = str(sample_user.id)

    event = MagicMock()
    event.type = "customer.subscription.deleted"
    event.data.object = {"customer": "cus_789"}
    mock_stripe.Webhook.construct_event.return_value = event

    customer_mock = MagicMock()
    customer_mock.metadata.get.return_value = user_id_str
    mock_stripe.Customer.retrieve.return_value = customer_mock

    sample_user.subscription_tier = "Premium"
    mock_result.scalar_one_or_none.return_value = sample_user

    await handle_webhook(mock_db, "payload_body", "sig_header")

    assert sample_user.subscription_tier == "Free"
    mock_db.commit.assert_awaited()
