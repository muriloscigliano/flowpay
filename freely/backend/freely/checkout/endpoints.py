"""Checkout and Order API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Cookie, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from freely.auth.dependencies import CurrentUser
from freely.cart.service import CartService
from freely.kit.db import get_db_session
from freely.models import Organization

from .schemas import (
    CheckoutResponse,
    CreateCheckoutRequest,
    OrderListResponse,
    OrderResponse,
)
from .service import OrderService

router = APIRouter(prefix="/checkout", tags=["checkout"])


async def get_user_organization(session: AsyncSession, user):
    """Get the user's first organization."""
    stmt = select(user.__class__).where(user.__class__.id == user.id).options(selectinload(user.__class__.organizations))
    result = await session.execute(stmt)
    user_with_orgs = result.scalar_one()

    if not user_with_orgs.organizations:
        raise HTTPException(status_code=404, detail="User has no organization")

    return user_with_orgs.organizations[0]


@router.post("", response_model=CheckoutResponse, status_code=201)
async def create_checkout(
    request: CreateCheckoutRequest,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    cart_session_id: str | None = Cookie(None, alias="freely_cart_session"),
) -> CheckoutResponse:
    """
    Create checkout from cart.

    Creates an order and Stripe PaymentIntent.
    Returns client_secret for frontend to complete payment.
    """
    user = auth_subject.subject if auth_subject.is_user else None

    # Get cart
    cart = await CartService.get_or_create_cart(
        session,
        user=user,
        session_id=cart_session_id,
    )

    # Reload cart with items
    cart = await CartService.get_cart_by_id(session, cart.id)

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Get organization (TODO: allow selecting organization)
    # For now, use first organization of first product's owner
    stmt = (
        select(Organization)
        .join("products")
        .where(Organization.id == cart.items[0].product.organization_id)
    )
    result = await session.execute(stmt)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Use customer info from request or user
    customer_email = request.customer_email
    customer_name = request.customer_name

    if user and not customer_email:
        customer_email = user.email
    if user and not customer_name:
        customer_name = user.username

    # Create order from cart
    shipping_address = None
    if request.shipping_address:
        shipping_address = {
            "line1": request.shipping_address.line1,
            "line2": request.shipping_address.line2,
            "city": request.shipping_address.city,
            "state": request.shipping_address.state,
            "postal_code": request.shipping_address.postal_code,
            "country": request.shipping_address.country,
        }

    order = await OrderService.create_order_from_cart(
        session,
        cart=cart,
        organization=organization,
        customer_email=customer_email,
        customer_name=customer_name,
        shipping_address=shipping_address,
        customer_notes=request.customer_notes,
    )

    # Create Stripe PaymentIntent
    client_secret = await OrderService.create_payment_intent(session, order)

    # Clear cart after creating order
    await CartService.clear_cart(session, cart)

    return CheckoutResponse(
        order_id=str(order.id),
        order_number=order.order_number,
        client_secret=client_secret,
        total_cents=order.total_cents,
        total_display=order.total_display,
    )


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> OrderListResponse:
    """List user's orders."""
    if not auth_subject.is_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user = auth_subject.subject

    orders, total = await OrderService.list_user_orders(
        session,
        user=user,
        page=page,
        page_size=page_size,
    )

    return OrderListResponse(
        orders=[OrderResponse.from_order(order) for order in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> OrderResponse:
    """Get order details."""
    user = auth_subject.subject if auth_subject.is_user else None

    order = await OrderService.get_order_by_id(session, UUID(order_id), user=user)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse.from_order(order)


@router.get("/orders/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    session: AsyncSession = get_db_session,
) -> OrderResponse:
    """
    Get order by order number.

    This is a public endpoint for order confirmation pages.
    """
    order = await OrderService.get_order_by_number(session, order_number)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderResponse.from_order(order)
