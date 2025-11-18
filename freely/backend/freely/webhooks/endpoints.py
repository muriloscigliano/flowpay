"""Stripe webhook handler."""

import stripe
from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from freely.checkout.service import OrderService
from freely.config import settings
from freely.kit.db import get_db_session

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    session: AsyncSession = get_db_session,
):
    """
    Handle Stripe webhook events.

    Events handled:
    - payment_intent.succeeded - Payment completed successfully
    - payment_intent.payment_failed - Payment failed
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    # Get raw body
    payload = await request.body()

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        await handle_payment_success(session, payment_intent)

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        await handle_payment_failed(session, payment_intent)

    return {"status": "success"}


async def handle_payment_success(session: AsyncSession, payment_intent: dict):
    """Handle successful payment."""
    payment_intent_id = payment_intent["id"]
    order_id = payment_intent.get("metadata", {}).get("order_id")

    if not order_id:
        return

    # Get order
    from uuid import UUID

    order = await OrderService.get_order_by_id(session, UUID(order_id))

    if not order:
        return

    # Confirm payment
    await OrderService.confirm_payment(session, order, payment_intent_id)

    # TODO: Send order confirmation email


async def handle_payment_failed(session: AsyncSession, payment_intent: dict):
    """Handle failed payment."""
    order_id = payment_intent.get("metadata", {}).get("order_id")

    if not order_id:
        return

    # Get order
    from uuid import UUID

    from freely.models import Order
    from sqlalchemy import select

    stmt = select(Order).where(Order.id == UUID(order_id))
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        return

    # Mark order as failed
    order.payment_status = "failed"
    await session.flush()

    # TODO: Send payment failed email
