"""Checkout and Order service layer."""

import secrets
from datetime import datetime, timezone
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from freely.config import settings
from freely.models import Cart, Order, OrderItem, Organization, User

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderService:
    """Service for managing orders."""

    @staticmethod
    def generate_order_number() -> str:
        """Generate unique order number."""
        # Format: ORD-XXXXXX (6 random hex characters)
        random_part = secrets.token_hex(3).upper()
        return f"ORD-{random_part}"

    @staticmethod
    async def create_order_from_cart(
        session: AsyncSession,
        cart: Cart,
        organization: Organization,
        customer_email: str | None = None,
        customer_name: str | None = None,
        shipping_address: dict | None = None,
        customer_notes: str | None = None,
    ) -> Order:
        """
        Create an order from a cart.

        Does NOT process payment - just creates the order record.
        Payment is handled by create_payment_intent.
        """
        # Load cart with items
        stmt = (
            select(Cart)
            .where(Cart.id == cart.id)
            .options(selectinload(Cart.items).selectinload("product"))
        )
        result = await session.execute(stmt)
        cart = result.scalar_one()

        if not cart.items:
            raise ValueError("Cart is empty")

        # Calculate totals
        subtotal_cents = cart.total_cents
        tax_cents = 0  # TODO: Calculate tax based on location
        shipping_cents = 0  # TODO: Calculate shipping
        total_cents = subtotal_cents + tax_cents + shipping_cents

        # Get user if cart has one
        user_id = cart.user_id

        # Create order
        order = Order(
            order_number=OrderService.generate_order_number(),
            user_id=user_id,
            organization_id=organization.id,
            customer_email=customer_email,
            customer_name=customer_name,
            subtotal_cents=subtotal_cents,
            tax_cents=tax_cents,
            shipping_cents=shipping_cents,
            total_cents=total_cents,
            currency="USD",
            payment_status="pending",
            customer_notes=customer_notes,
        )

        # Add shipping address if provided
        if shipping_address:
            order.shipping_address_line1 = shipping_address.get("line1")
            order.shipping_address_line2 = shipping_address.get("line2")
            order.shipping_city = shipping_address.get("city")
            order.shipping_state = shipping_address.get("state")
            order.shipping_postal_code = shipping_address.get("postal_code")
            order.shipping_country = shipping_address.get("country", "US")

        session.add(order)
        await session.flush()

        # Create order items (snapshot from cart)
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=cart_item.product.name if cart_item.product else "Deleted Product",
                product_slug=cart_item.product.slug if cart_item.product else "deleted",
                product_description=(
                    cart_item.product.description if cart_item.product else None
                ),
                quantity=cart_item.quantity,
                price_cents=cart_item.price_cents,
                currency=cart_item.currency,
            )
            session.add(order_item)

        await session.flush()
        return order

    @staticmethod
    async def create_payment_intent(
        session: AsyncSession,
        order: Order,
    ) -> str:
        """
        Create Stripe PaymentIntent for an order.

        Returns the client_secret for frontend to complete payment.
        """
        if not settings.STRIPE_SECRET_KEY:
            raise ValueError("Stripe is not configured")

        # Create PaymentIntent
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=order.total_cents,
                currency=order.currency.lower(),
                metadata={
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                },
                automatic_payment_methods={"enabled": True},
            )

            # Save PaymentIntent ID to order
            order.stripe_payment_intent_id = payment_intent.id
            await session.flush()

            return payment_intent.client_secret

        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")

    @staticmethod
    async def confirm_payment(
        session: AsyncSession,
        order: Order,
        payment_intent_id: str,
    ) -> Order:
        """
        Confirm payment and mark order as paid.

        Called after Stripe webhook confirms payment.
        """
        # Verify payment intent matches
        if order.stripe_payment_intent_id != payment_intent_id:
            raise ValueError("Payment intent ID mismatch")

        # Update order status
        order.payment_status = "paid"
        order.paid_at = datetime.now(timezone.utc).isoformat()

        await session.flush()
        return order

    @staticmethod
    async def get_order_by_id(
        session: AsyncSession,
        order_id: UUID,
        user: User | None = None,
    ) -> Order | None:
        """Get an order by ID."""
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .where(Order.deleted_at.is_(None))
            .options(selectinload(Order.items))
        )

        if user:
            stmt = stmt.where(Order.user_id == user.id)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_order_by_number(
        session: AsyncSession,
        order_number: str,
    ) -> Order | None:
        """Get an order by order number."""
        stmt = (
            select(Order)
            .where(Order.order_number == order_number)
            .where(Order.deleted_at.is_(None))
            .options(selectinload(Order.items))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_user_orders(
        session: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        """List orders for a user with pagination."""
        from sqlalchemy import func

        # Base query
        stmt = select(Order).where(Order.user_id == user.id).where(Order.deleted_at.is_(None))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await session.scalar(count_stmt) or 0

        # Add pagination and ordering
        stmt = (
            stmt.options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await session.execute(stmt)
        orders = list(result.scalars().all())

        return orders, total

    @staticmethod
    async def list_organization_orders(
        session: AsyncSession,
        organization: Organization,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        """List orders for an organization with pagination."""
        from sqlalchemy import func

        # Base query
        stmt = (
            select(Order)
            .where(Order.organization_id == organization.id)
            .where(Order.deleted_at.is_(None))
        )

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await session.scalar(count_stmt) or 0

        # Add pagination and ordering
        stmt = (
            stmt.options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await session.execute(stmt)
        orders = list(result.scalars().all())

        return orders, total
