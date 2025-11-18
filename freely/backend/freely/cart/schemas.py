"""Cart schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class AddToCartRequest(BaseModel):
    """Schema for adding product to cart."""

    product_id: str
    quantity: int = Field(default=1, ge=1)


class UpdateCartItemRequest(BaseModel):
    """Schema for updating cart item quantity."""

    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    """Schema for cart item response."""

    id: str
    product_id: str | None
    product_name: str
    product_slug: str
    product_image_url: str | None
    quantity: int
    price_cents: int
    currency: str
    price_display: str
    subtotal_cents: int
    subtotal_display: str
    created_at: datetime

    @classmethod
    def from_cart_item(cls, cart_item) -> "CartItemResponse":
        """Create from CartItem model."""
        # Get product info (handle if product is deleted)
        try:
            product_name = cart_item.product.name if cart_item.product else "Deleted Product"
            product_slug = cart_item.product.slug if cart_item.product else "deleted"
            product_image_url = (
                cart_item.product.image_urls[0]
                if cart_item.product and cart_item.product.image_urls
                else None
            )
        except Exception:
            product_name = "Deleted Product"
            product_slug = "deleted"
            product_image_url = None

        return cls(
            id=str(cart_item.id),
            product_id=str(cart_item.product_id) if cart_item.product_id else None,
            product_name=product_name,
            product_slug=product_slug,
            product_image_url=product_image_url,
            quantity=cart_item.quantity,
            price_cents=cart_item.price_cents,
            currency=cart_item.currency,
            price_display=cart_item.price_display,
            subtotal_cents=cart_item.subtotal_cents,
            subtotal_display=cart_item.subtotal_display,
            created_at=cart_item.created_at,
        )

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    """Schema for cart response."""

    id: str
    items: list[CartItemResponse]
    total_cents: int
    total_display: str
    item_count: int
    created_at: datetime

    @classmethod
    def from_cart(cls, cart) -> "CartResponse":
        """Create from Cart model."""
        # Load items
        items = []
        try:
            items = [CartItemResponse.from_cart_item(item) for item in cart.items if not item.deleted_at]
        except Exception:
            # Items not loaded
            pass

        return cls(
            id=str(cart.id),
            items=items,
            total_cents=cart.total_cents,
            total_display=cart.total_display,
            item_count=cart.item_count,
            created_at=cart.created_at,
        )

    model_config = {"from_attributes": True}
