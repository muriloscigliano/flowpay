"""Product and Category schemas for API validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    id: str
    organization_id: str
    created_at: datetime

    @classmethod
    def from_category(cls, category) -> "CategoryResponse":
        """Create from Category model."""
        return cls(
            id=str(category.id),
            name=category.name,
            slug=category.slug,
            description=category.description,
            organization_id=str(category.organization_id),
            created_at=category.created_at,
        )

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    """Base product schema."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    price_cents: int = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    image_urls: list[str] | None = None
    stock_available: int | None = Field(None, ge=0)
    is_available: bool = True
    is_digital: bool = False
    category_ids: list[str] = Field(default_factory=list)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency is uppercase ISO 4217."""
        return v.upper()


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    name: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    price_cents: int | None = Field(None, ge=0)
    currency: str | None = Field(None, min_length=3, max_length=3)
    image_urls: list[str] | None = None
    stock_available: int | None = Field(None, ge=0)
    is_available: bool | None = None
    is_digital: bool | None = None
    category_ids: list[str] | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str | None:
        """Validate currency is uppercase ISO 4217."""
        if v is None:
            return v
        return v.upper()


class ProductResponse(ProductBase):
    """Schema for product response."""

    id: str
    organization_id: str
    created_at: datetime
    price_display: str
    categories: list[CategoryResponse] = Field(default_factory=list)

    @classmethod
    def from_product(cls, product) -> "ProductResponse":
        """Create from Product model."""
        # Handle categories if loaded
        categories = []
        try:
            categories = [CategoryResponse.from_category(cat) for cat in product.categories]
        except Exception:
            # Categories not loaded (lazy='raise'), skip
            pass

        return cls(
            id=str(product.id),
            name=product.name,
            slug=product.slug,
            description=product.description,
            price_cents=product.price_cents,
            currency=product.currency,
            image_urls=product.image_urls or [],
            stock_available=product.stock_available,
            is_available=product.is_available,
            is_digital=product.is_digital,
            organization_id=str(product.organization_id),
            created_at=product.created_at,
            price_display=product.price_display,
            categories=categories,
            category_ids=[str(cat.id) for cat in product.categories] if categories else [],
        )

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Schema for paginated product list."""

    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
