"""Cart API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Cookie, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from freely.auth.dependencies import CurrentUser
from freely.kit.db import get_db_session
from freely.models import User
from freely.product.service import ProductService

from .schemas import AddToCartRequest, CartResponse, UpdateCartItemRequest
from .service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


def get_session_id(freely_cart_session: str | None = Cookie(None)) -> str | None:
    """Get cart session ID from cookie."""
    return freely_cart_session


@router.get("", response_model=CartResponse)
async def get_cart(
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    cart_session_id: str | None = Cookie(None, alias="freely_cart_session"),
) -> CartResponse:
    """Get user's cart."""
    user = auth_subject.subject if auth_subject.is_user else None

    cart = await CartService.get_or_create_cart(
        session,
        user=user,
        session_id=cart_session_id,
    )

    return CartResponse.from_cart(cart)


@router.post("/items", response_model=CartResponse, status_code=201)
async def add_to_cart(
    request: AddToCartRequest,
    response: Response,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    cart_session_id: str | None = Cookie(None, alias="freely_cart_session"),
) -> CartResponse:
    """Add product to cart."""
    user = auth_subject.subject if auth_subject.is_user else None

    # Generate session ID if needed (for anonymous users)
    if not user and not cart_session_id:
        import secrets

        cart_session_id = secrets.token_urlsafe(32)
        response.set_cookie(
            key="freely_cart_session",
            value=cart_session_id,
            httponly=True,
            max_age=60 * 60 * 24 * 30,  # 30 days
        )

    # Get or create cart
    cart = await CartService.get_or_create_cart(
        session,
        user=user,
        session_id=cart_session_id,
    )

    # Get product
    product = await ProductService.get_product_by_id(session, UUID(request.product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product.is_available:
        raise HTTPException(status_code=400, detail="Product is not available")

    # Check stock
    if product.stock_available is not None:
        if product.stock_available < request.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Only {product.stock_available} available.",
            )

    # Add to cart
    await CartService.add_to_cart(
        session,
        cart=cart,
        product=product,
        quantity=request.quantity,
    )

    # Reload cart
    cart = await CartService.get_cart_by_id(session, cart.id)

    return CartResponse.from_cart(cart)


@router.patch("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: str,
    request: UpdateCartItemRequest,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    cart_session_id: str | None = Cookie(None, alias="freely_cart_session"),
) -> CartResponse:
    """Update cart item quantity."""
    user = auth_subject.subject if auth_subject.is_user else None

    # Get cart
    cart = await CartService.get_or_create_cart(
        session,
        user=user,
        session_id=cart_session_id,
    )

    # Get cart item
    cart_item = await CartService.get_cart_item_by_id(session, UUID(item_id), cart)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Update quantity
    await CartService.update_cart_item_quantity(session, cart_item, request.quantity)

    # Reload cart
    cart = await CartService.get_cart_by_id(session, cart.id)

    return CartResponse.from_cart(cart)


@router.delete("/items/{item_id}", status_code=204)
async def remove_from_cart(
    item_id: str,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    cart_session_id: str | None = Cookie(None, alias="freely_cart_session"),
) -> None:
    """Remove item from cart."""
    user = auth_subject.subject if auth_subject.is_user else None

    # Get cart
    cart = await CartService.get_or_create_cart(
        session,
        user=user,
        session_id=cart_session_id,
    )

    # Get cart item
    cart_item = await CartService.get_cart_item_by_id(session, UUID(item_id), cart)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Remove from cart
    await CartService.remove_from_cart(session, cart_item)


@router.delete("", status_code=204)
async def clear_cart(
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    cart_session_id: str | None = Cookie(None, alias="freely_cart_session"),
) -> None:
    """Clear all items from cart."""
    user = auth_subject.subject if auth_subject.is_user else None

    # Get cart
    cart = await CartService.get_or_create_cart(
        session,
        user=user,
        session_id=cart_session_id,
    )

    # Clear cart
    await CartService.clear_cart(session, cart)
