import uuid

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User


def _configure_stripe():
    if settings.stripe_secret_key:
        stripe.api_key = settings.stripe_secret_key


async def create_checkout_session(
    db: AsyncSession, user_id: uuid.UUID, success_url: str, cancel_url: str
) -> str:
    _configure_stripe()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    # Create Stripe customer if needed
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"meridian_user_id": str(user_id)},
        )
        user.stripe_customer_id = customer.id
        await db.commit()

    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": settings.stripe_premium_price_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


async def create_portal_session(db: AsyncSession, user_id: uuid.UUID, return_url: str) -> str:
    _configure_stripe()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    if not user.stripe_customer_id:
        raise ValueError("No Stripe customer found")

    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=return_url,
    )
    return session.url


async def handle_webhook(db: AsyncSession, payload: str, signature: str) -> None:
    _configure_stripe()

    event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)

    if event.type == "checkout.session.completed":
        session = event.data.object
        customer_id = session.get("customer")
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            user_id_str = customer.metadata.get("meridian_user_id")
            if user_id_str:
                result = await db.execute(select(User).where(User.id == uuid.UUID(user_id_str)))
                user = result.scalar_one_or_none()
                if user:
                    user.subscription_tier = "Premium"
                    await db.commit()

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        customer_id = subscription.get("customer")
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            user_id_str = customer.metadata.get("meridian_user_id")
            if user_id_str:
                result = await db.execute(select(User).where(User.id == uuid.UUID(user_id_str)))
                user = result.scalar_one_or_none()
                if user:
                    user.subscription_tier = "Free"
                    await db.commit()
