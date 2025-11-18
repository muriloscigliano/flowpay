"""Checkout and Order schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class ShippingAddressRequest(BaseModel):
    """Shipping address for checkout."""

    line1: str = Field(..., min_length=1)
    line2: str | None = None
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    postal_code: str = Field(..., min_length=1)
    country: str = Field(default="US", min_length=2, max_length=2)


class CreateCheckoutRequest(BaseModel):
    """Schema for creating a checkout session."""

    customer_email: str | None = None
    customer_name: str | None = None
    shipping_address: ShippingAddressRequest | None = None
    customer_notes: str | None = None


class CheckoutResponse(BaseModel):
    """Schema for checkout response."""

    order_id: str
    order_number: str
    client_secret: str  # Stripe PaymentIntent client secret
    total_cents: int
    total_display: str


class OrderItemResponse(BaseModel):
    """Schema for order item response."""

    id: str
    product_id: str | None
    product_name: str
    product_slug: str
    quantity: int
    price_cents: int
    currency: str
    price_display: str
    subtotal_cents: int
    subtotal_display: str

    @classmethod
    def from_order_item(cls, order_item) -> "OrderItemResponse":
        """Create from OrderItem model."""
        return cls(
            id=str(order_item.id),
            product_id=str(order_item.product_id) if order_item.product_id else None,
            product_name=order_item.product_name,
            product_slug=order_item.product_slug,
            quantity=order_item.quantity,
            price_cents=order_item.price_cents,
            currency=order_item.currency,
            price_display=order_item.price_display,
            subtotal_cents=order_item.subtotal_cents,
            subtotal_display=order_item.subtotal_display,
        )

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """Schema for order response."""

    id: str
    order_number: str
    user_id: str | None
    organization_id: str
    customer_email: str | None
    customer_name: str | None
    items: list[OrderItemResponse]
    subtotal_cents: int
    tax_cents: int
    shipping_cents: int
    total_cents: int
    currency: str
    total_display: str
    subtotal_display: str
    payment_status: str
    fulfillment_status: str
    created_at: datetime
    paid_at: str | None

    @classmethod
    def from_order(cls, order) -> "OrderResponse":
        """Create from Order model."""
        # Load items
        items = []
        try:
            items = [OrderItemResponse.from_order_item(item) for item in order.items]
        except Exception:
            # Items not loaded
            pass

        return cls(
            id=str(order.id),
            order_number=order.order_number,
            user_id=str(order.user_id) if order.user_id else None,
            organization_id=str(order.organization_id),
            customer_email=order.customer_email,
            customer_name=order.customer_name,
            items=items,
            subtotal_cents=order.subtotal_cents,
            tax_cents=order.tax_cents,
            shipping_cents=order.shipping_cents,
            total_cents=order.total_cents,
            currency=order.currency,
            total_display=order.total_display,
            subtotal_display=order.subtotal_display,
            payment_status=order.payment_status,
            fulfillment_status=order.fulfillment_status,
            created_at=order.created_at,
            paid_at=order.paid_at,
        )

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    """Schema for paginated order list."""

    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int
