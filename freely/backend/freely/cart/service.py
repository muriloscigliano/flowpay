"""Cart service layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from freely.models import Cart, CartItem, Product, User


class CartService:
    """Service for managing shopping carts."""

    @staticmethod
    async def get_or_create_cart(
        session: AsyncSession,
        user: User | None = None,
        session_id: str | None = None,
    ) -> Cart:
        """
        Get or create a cart for user or session.

        For authenticated users, uses user_id.
        For anonymous users, uses session_id.
        """
        if user:
            # Get user's cart
            stmt = (
                select(Cart)
                .where(Cart.user_id == user.id)
                .where(Cart.deleted_at.is_(None))
                .options(selectinload(Cart.items).selectinload(CartItem.product))
            )
            result = await session.execute(stmt)
            cart = result.scalar_one_or_none()

            if not cart:
                cart = Cart(user_id=user.id)
                session.add(cart)
                await session.flush()

            return cart
        elif session_id:
            # Get session cart
            stmt = (
                select(Cart)
                .where(Cart.session_id == session_id)
                .where(Cart.deleted_at.is_(None))
                .options(selectinload(Cart.items).selectinload(CartItem.product))
            )
            result = await session.execute(stmt)
            cart = result.scalar_one_or_none()

            if not cart:
                cart = Cart(session_id=session_id)
                session.add(cart)
                await session.flush()

            return cart
        else:
            raise ValueError("Either user or session_id must be provided")

    @staticmethod
    async def get_cart_by_id(session: AsyncSession, cart_id: UUID) -> Cart | None:
        """Get a cart by ID."""
        stmt = (
            select(Cart)
            .where(Cart.id == cart_id)
            .where(Cart.deleted_at.is_(None))
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_to_cart(
        session: AsyncSession,
        cart: Cart,
        product: Product,
        quantity: int = 1,
    ) -> CartItem:
        """
        Add a product to cart.

        If product already exists, increase quantity.
        Otherwise, create new cart item.
        """
        # Load cart items if not loaded
        stmt = (
            select(Cart)
            .where(Cart.id == cart.id)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        result = await session.execute(stmt)
        cart = result.scalar_one()

        # Check if product already in cart
        existing_item = None
        for item in cart.items:
            if item.product_id == product.id:
                existing_item = item
                break

        if existing_item:
            # Increase quantity
            existing_item.quantity += quantity
            await session.flush()
            return existing_item
        else:
            # Create new cart item (snapshot price)
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=quantity,
                price_cents=product.price_cents,
                currency=product.currency,
            )
            session.add(cart_item)
            await session.flush()

            # Refresh to load product relationship
            await session.refresh(cart_item, ["product"])
            return cart_item

    @staticmethod
    async def update_cart_item_quantity(
        session: AsyncSession,
        cart_item: CartItem,
        quantity: int,
    ) -> CartItem:
        """Update cart item quantity."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        cart_item.quantity = quantity
        await session.flush()
        return cart_item

    @staticmethod
    async def remove_from_cart(
        session: AsyncSession,
        cart_item: CartItem,
    ) -> None:
        """Remove an item from cart."""
        from datetime import datetime, timezone

        cart_item.deleted_at = datetime.now(timezone.utc)
        await session.flush()

    @staticmethod
    async def get_cart_item_by_id(
        session: AsyncSession,
        cart_item_id: UUID,
        cart: Cart,
    ) -> CartItem | None:
        """Get a cart item by ID (must belong to the cart)."""
        stmt = (
            select(CartItem)
            .where(CartItem.id == cart_item_id)
            .where(CartItem.cart_id == cart.id)
            .where(CartItem.deleted_at.is_(None))
            .options(selectinload(CartItem.product))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def clear_cart(session: AsyncSession, cart: Cart) -> None:
        """Remove all items from cart."""
        from datetime import datetime, timezone

        # Load cart items if not loaded
        stmt = (
            select(Cart)
            .where(Cart.id == cart.id)
            .options(selectinload(Cart.items))
        )
        result = await session.execute(stmt)
        cart = result.scalar_one()

        # Soft delete all items
        now = datetime.now(timezone.utc)
        for item in cart.items:
            item.deleted_at = now

        await session.flush()

    @staticmethod
    async def merge_carts(
        session: AsyncSession,
        session_cart: Cart,
        user_cart: Cart,
    ) -> Cart:
        """
        Merge session cart into user cart (for login).

        - Add session cart items to user cart
        - Delete session cart
        - Return user cart
        """
        # Load both carts with items
        stmt = (
            select(Cart)
            .where(Cart.id.in_([session_cart.id, user_cart.id]))
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        result = await session.execute(stmt)
        carts = {cart.id: cart for cart in result.scalars().all()}

        session_cart = carts[session_cart.id]
        user_cart = carts[user_cart.id]

        # Merge items
        for session_item in session_cart.items:
            # Check if user cart already has this product
            existing = None
            for user_item in user_cart.items:
                if user_item.product_id == session_item.product_id:
                    existing = user_item
                    break

            if existing:
                # Increase quantity
                existing.quantity += session_item.quantity
            else:
                # Move item to user cart
                session_item.cart_id = user_cart.id

        # Delete session cart
        from datetime import datetime, timezone

        session_cart.deleted_at = datetime.now(timezone.utc)

        await session.flush()

        # Reload user cart
        stmt = (
            select(Cart)
            .where(Cart.id == user_cart.id)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        result = await session.execute(stmt)
        return result.scalar_one()
