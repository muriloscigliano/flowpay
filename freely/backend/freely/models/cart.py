"""Shopping cart models."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import RecordModel

if TYPE_CHECKING:
    from .product import Product
    from .user import User


class Cart(RecordModel):
    """
    Shopping cart.

    Can be associated with a user (authenticated) or session (anonymous).
    """

    __tablename__ = "carts"

    # User (nullable for anonymous carts)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    user: Mapped["User | None"] = relationship("User", lazy="raise")

    # Session ID for anonymous carts
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Relationships
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Cart id={self.id} user_id={self.user_id}>"

    @property
    def total_cents(self) -> int:
        """Calculate total price in cents."""
        try:
            return sum(item.subtotal_cents for item in self.items)
        except Exception:
            # Items not loaded
            return 0

    @property
    def total_display(self) -> str:
        """Display total in dollars."""
        dollars = self.total_cents / 100
        return f"${dollars:.2f}"

    @property
    def item_count(self) -> int:
        """Total number of items in cart."""
        try:
            return sum(item.quantity for item in self.items)
        except Exception:
            # Items not loaded
            return 0


class CartItem(RecordModel):
    """
    Item in a shopping cart.
    """

    __tablename__ = "cart_items"

    cart_id: Mapped[UUID] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items", lazy="raise")

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    product: Mapped["Product"] = relationship("Product", lazy="raise")

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Price snapshot at time of adding to cart (in cents)
    # Prevents price changes from affecting cart
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    def __repr__(self) -> str:
        return f"<CartItem id={self.id} product_id={self.product_id} quantity={self.quantity}>"

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
