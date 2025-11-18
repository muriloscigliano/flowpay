"""Order models for completed purchases."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import RecordModel

if TYPE_CHECKING:
    from .organization import Organization
    from .product import Product
    from .user import User


class Order(RecordModel):
    """
    Completed order.

    Created after successful payment via Stripe.
    """

    __tablename__ = "orders"

    # Order number (human-readable, e.g., "ORD-1234")
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # User (nullable for guest checkout)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    user: Mapped["User | None"] = relationship("User", lazy="raise")

    # Organization (merchant)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    organization: Mapped["Organization"] = relationship("Organization", lazy="raise")

    # Customer Info (for guest checkout)
    customer_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Pricing
    subtotal_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    tax_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shipping_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Payment Status
    payment_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, paid, failed, refunded

    # Stripe
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    stripe_charge_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Shipping Address
    shipping_address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipping_address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipping_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shipping_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shipping_postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    shipping_country: Mapped[str | None] = mapped_column(String(2), nullable=True)  # ISO 3166-1 alpha-2

    # Notes
    customer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Fulfillment
    fulfillment_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unfulfilled"
    )  # unfulfilled, fulfilled, shipped, delivered

    # Timestamps
    paid_at: Mapped[str | None] = mapped_column(String, nullable=True)  # ISO datetime
    fulfilled_at: Mapped[str | None] = mapped_column(String, nullable=True)  # ISO datetime

    # Relationships
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} order_number={self.order_number}>"

    @property
    def total_display(self) -> str:
        """Display total in dollars."""
        dollars = self.total_cents / 100
        return f"${dollars:.2f}"

    @property
    def subtotal_display(self) -> str:
        """Display subtotal in dollars."""
        dollars = self.subtotal_cents / 100
        return f"${dollars:.2f}"


class OrderItem(RecordModel):
    """
    Item in an order.

    Snapshot of product at time of purchase.
    """

    __tablename__ = "order_items"

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    order: Mapped["Order"] = relationship("Order", back_populates="items", lazy="raise")

    product_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    product: Mapped["Product | None"] = relationship("Product", lazy="raise")

    # Product snapshot (in case product is deleted/changed)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_slug: Mapped[str] = mapped_column(String(200), nullable=False)
    product_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    def __repr__(self) -> str:
        return f"<OrderItem id={self.id} product_name={self.product_name} quantity={self.quantity}>"

    @property
    def subtotal_cents(self) -> int:
        """Calculate subtotal (price * quantity) in cents."""
        return self.price_cents * self.quantity

    @property
    def subtotal_display(self) -> str:
        """Display subtotal in dollars."""
        dollars = self.subtotal_cents / 100
        return f"${dollars:.2f}"

    @property
    def price_display(self) -> str:
        """Display unit price in dollars."""
        dollars = self.price_cents / 100
        return f"${dollars:.2f}"
