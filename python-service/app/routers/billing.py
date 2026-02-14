import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_id
from app.db.database import get_db
from app.models.billing_schemas import CheckoutRequest, PortalRequest
from app.services import billing_service

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/checkout")
async def create_checkout(
    request: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    url = await billing_service.create_checkout_session(
        db, user_id, request.success_url, request.cancel_url
    )
    return {"url": url}


@router.post("/portal")
async def create_portal(
    request: PortalRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    url = await billing_service.create_portal_session(db, user_id, request.return_url)
    return {"url": url}


@router.post("/webhook")
async def webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    signature = request.headers.get("Stripe-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    payload = await request.body()
    try:
        await billing_service.handle_webhook(db, payload.decode(), signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")
    return {"status": "ok"}
