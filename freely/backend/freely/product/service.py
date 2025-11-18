"""Product and Category service layer."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from freely.models import Category, Organization, Product


class ProductService:
    """Service for managing products."""

    @staticmethod
    async def create_product(
        session: AsyncSession,
        organization: Organization,
        name: str,
        slug: str,
        price_cents: int,
        description: str | None = None,
        currency: str = "USD",
        image_urls: list[str] | None = None,
        stock_available: int | None = None,
        is_available: bool = True,
        is_digital: bool = False,
        category_ids: list[UUID] | None = None,
    ) -> Product:
        """Create a new product."""
        product = Product(
            name=name,
            slug=slug,
            description=description,
            price_cents=price_cents,
            currency=currency,
            image_urls=image_urls,
            stock_available=stock_available,
            is_available=is_available,
            is_digital=is_digital,
            organization_id=organization.id,
        )

        session.add(product)
        await session.flush()

        # Add categories if provided
        if category_ids:
            categories = await CategoryService.get_categories_by_ids(
                session, category_ids, organization
            )
            product.categories = categories
            await session.flush()

        return product

    @staticmethod
    async def get_product_by_id(
        session: AsyncSession, product_id: UUID, organization: Organization | None = None
    ) -> Product | None:
        """Get a product by ID."""
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .where(Product.deleted_at.is_(None))
            .options(selectinload(Product.categories))
        )

        if organization:
            stmt = stmt.where(Product.organization_id == organization.id)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_product_by_slug(
        session: AsyncSession, slug: str, organization: Organization
    ) -> Product | None:
        """Get a product by slug."""
        stmt = (
            select(Product)
            .where(Product.slug == slug)
            .where(Product.organization_id == organization.id)
            .where(Product.deleted_at.is_(None))
            .options(selectinload(Product.categories))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_products(
        session: AsyncSession,
        organization: Organization | None = None,
        category_id: UUID | None = None,
        search_query: str | None = None,
        is_available: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:
        """List products with filtering and pagination."""
        # Base query
        stmt = select(Product).where(Product.deleted_at.is_(None))

        if organization:
            stmt = stmt.where(Product.organization_id == organization.id)

        if is_available is not None:
            stmt = stmt.where(Product.is_available == is_available)

        # Search by name or description
        if search_query:
            search_filter = or_(
                Product.name.ilike(f"%{search_query}%"),
                Product.description.ilike(f"%{search_query}%"),
            )
            stmt = stmt.where(search_filter)

        # Filter by category
        if category_id:
            stmt = stmt.join(Product.categories).where(Category.id == category_id)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await session.scalar(count_stmt) or 0

        # Add pagination
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        # Load categories relationship
        stmt = stmt.options(selectinload(Product.categories))

        # Order by created_at desc
        stmt = stmt.order_by(Product.created_at.desc())

        result = await session.execute(stmt)
        products = list(result.scalars().all())

        return products, total

    @staticmethod
    async def update_product(
        session: AsyncSession,
        product: Product,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        price_cents: int | None = None,
        currency: str | None = None,
        image_urls: list[str] | None = None,
        stock_available: int | None = None,
        is_available: bool | None = None,
        is_digital: bool | None = None,
        category_ids: list[UUID] | None = None,
    ) -> Product:
        """Update a product."""
        if name is not None:
            product.name = name
        if slug is not None:
            product.slug = slug
        if description is not None:
            product.description = description
        if price_cents is not None:
            product.price_cents = price_cents
        if currency is not None:
            product.currency = currency
        if image_urls is not None:
            product.image_urls = image_urls
        if stock_available is not None:
            product.stock_available = stock_available
        if is_available is not None:
            product.is_available = is_available
        if is_digital is not None:
            product.is_digital = is_digital

        # Update categories if provided
        if category_ids is not None:
            stmt = select(Organization).where(Organization.id == product.organization_id)
            result = await session.execute(stmt)
            organization = result.scalar_one()

            categories = await CategoryService.get_categories_by_ids(
                session, category_ids, organization
            )
            product.categories = categories

        await session.flush()
        return product

    @staticmethod
    async def delete_product(session: AsyncSession, product: Product) -> None:
        """Soft delete a product."""
        from datetime import datetime, timezone

        product.deleted_at = datetime.now(timezone.utc)
        await session.flush()


class CategoryService:
    """Service for managing categories."""

    @staticmethod
    async def create_category(
        session: AsyncSession,
        organization: Organization,
        name: str,
        slug: str,
        description: str | None = None,
    ) -> Category:
        """Create a new category."""
        category = Category(
            name=name,
            slug=slug,
            description=description,
            organization_id=organization.id,
        )

        session.add(category)
        await session.flush()
        return category

    @staticmethod
    async def get_category_by_id(
        session: AsyncSession, category_id: UUID, organization: Organization | None = None
    ) -> Category | None:
        """Get a category by ID."""
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .where(Category.deleted_at.is_(None))
        )

        if organization:
            stmt = stmt.where(Category.organization_id == organization.id)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_category_by_slug(
        session: AsyncSession, slug: str, organization: Organization
    ) -> Category | None:
        """Get a category by slug."""
        stmt = (
            select(Category)
            .where(Category.slug == slug)
            .where(Category.organization_id == organization.id)
            .where(Category.deleted_at.is_(None))
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_categories_by_ids(
        session: AsyncSession, category_ids: list[UUID], organization: Organization
    ) -> list[Category]:
        """Get multiple categories by IDs."""
        stmt = (
            select(Category)
            .where(Category.id.in_(category_ids))
            .where(Category.organization_id == organization.id)
            .where(Category.deleted_at.is_(None))
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def list_categories(
        session: AsyncSession,
        organization: Organization | None = None,
    ) -> list[Category]:
        """List all categories for an organization."""
        stmt = select(Category).where(Category.deleted_at.is_(None))

        if organization:
            stmt = stmt.where(Category.organization_id == organization.id)

        stmt = stmt.order_by(Category.name.asc())

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_category(
        session: AsyncSession,
        category: Category,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
    ) -> Category:
        """Update a category."""
        if name is not None:
            category.name = name
        if slug is not None:
            category.slug = slug
        if description is not None:
            category.description = description

        await session.flush()
        return category

    @staticmethod
    async def delete_category(session: AsyncSession, category: Category) -> None:
        """Soft delete a category."""
        from datetime import datetime, timezone

        category.deleted_at = datetime.now(timezone.utc)
        await session.flush()
