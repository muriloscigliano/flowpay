"""Product and Category models."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model, RecordModel

if TYPE_CHECKING:
    from .organization import Organization


# Association table for many-to-many Product <-> Category
product_categories = Table(
    "product_categories",
    Model.metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Category(RecordModel):
    """
    Product category for organization and filtering.

    Examples: Electronics, Clothing, Food & Beverage, Digital Products
    """

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Organization (multi-tenant)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    organization: Mapped["Organization"] = relationship("Organization", lazy="raise")

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product",
        secondary="product_categories",
        back_populates="categories",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} slug={self.slug}>"


class Product(RecordModel):
    """
    Product for sale.

    Can be physical goods, digital products, or services.
    """

    __tablename__ = "products"

    # Basic Info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pricing (stored in cents to avoid floating point issues)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")  # ISO 4217

    # Images (array of S3/MinIO URLs)
    image_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Inventory
    stock_available: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = unlimited
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Digital product flag
    is_digital: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Organization (multi-tenant)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    organization: Mapped["Organization"] = relationship("Organization", lazy="raise")

    # Relationships
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary="product_categories",
        back_populates="products",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} slug={self.slug}>"

    @property
    def price_display(self) -> str:
        """Display price in human-readable format."""
        dollars = self.price_cents / 100
        return f"${dollars:.2f}"
