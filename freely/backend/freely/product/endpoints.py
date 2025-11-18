"""Product and Category API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from freely.auth.dependencies import CurrentUser
from freely.kit.db import get_db_session
from freely.models import User

from .schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from .service import CategoryService, ProductService

router = APIRouter(prefix="/products", tags=["products"])


async def get_user_organization(session: AsyncSession, user: User):
    """Get the user's first organization. Raises 404 if no organization."""
    from sqlalchemy import select

    from freely.models import Organization

    # Reload user with organizations
    stmt = select(User).where(User.id == user.id).options(selectinload(User.organizations))
    result = await session.execute(stmt)
    user_with_orgs = result.scalar_one()

    if not user_with_orgs.organizations:
        raise HTTPException(status_code=404, detail="User has no organization")

    return user_with_orgs.organizations[0]


# === Category Endpoints ===


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    request: CategoryCreate,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> CategoryResponse:
    """Create a new category."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    # Check if slug already exists
    existing = await CategoryService.get_category_by_slug(session, request.slug, organization)
    if existing:
        raise HTTPException(status_code=400, detail="Category with this slug already exists")

    category = await CategoryService.create_category(
        session,
        organization=organization,
        name=request.name,
        slug=request.slug,
        description=request.description,
    )

    return CategoryResponse.from_category(category)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> list[CategoryResponse]:
    """List all categories for the user's organization."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    categories = await CategoryService.list_categories(session, organization=organization)
    return [CategoryResponse.from_category(cat) for cat in categories]


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> CategoryResponse:
    """Get a category by ID."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    category = await CategoryService.get_category_by_id(
        session, UUID(category_id), organization=organization
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return CategoryResponse.from_category(category)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    request: CategoryUpdate,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> CategoryResponse:
    """Update a category."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    category = await CategoryService.get_category_by_id(
        session, UUID(category_id), organization=organization
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check slug uniqueness if changing
    if request.slug and request.slug != category.slug:
        existing = await CategoryService.get_category_by_slug(session, request.slug, organization)
        if existing:
            raise HTTPException(status_code=400, detail="Category with this slug already exists")

    category = await CategoryService.update_category(
        session,
        category,
        name=request.name,
        slug=request.slug,
        description=request.description,
    )

    return CategoryResponse.from_category(category)


@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> None:
    """Delete a category."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    category = await CategoryService.get_category_by_id(
        session, UUID(category_id), organization=organization
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await CategoryService.delete_category(session, category)


# === Product Endpoints ===


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    request: ProductCreate,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> ProductResponse:
    """Create a new product."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    # Check if slug already exists
    existing = await ProductService.get_product_by_slug(session, request.slug, organization)
    if existing:
        raise HTTPException(status_code=400, detail="Product with this slug already exists")

    # Convert category_ids to UUIDs
    category_ids = [UUID(cid) for cid in request.category_ids] if request.category_ids else None

    product = await ProductService.create_product(
        session,
        organization=organization,
        name=request.name,
        slug=request.slug,
        description=request.description,
        price_cents=request.price_cents,
        currency=request.currency,
        image_urls=request.image_urls,
        stock_available=request.stock_available,
        is_available=request.is_available,
        is_digital=request.is_digital,
        category_ids=category_ids,
    )

    return ProductResponse.from_product(product)


@router.get("/", response_model=ProductListResponse)
async def list_products(
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
    category_id: str | None = Query(None, description="Filter by category ID"),
    search: str | None = Query(None, description="Search by name or description"),
    is_available: bool | None = Query(None, description="Filter by availability"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ProductListResponse:
    """List products with filtering and pagination."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    category_uuid = UUID(category_id) if category_id else None

    products, total = await ProductService.list_products(
        session,
        organization=organization,
        category_id=category_uuid,
        search_query=search,
        is_available=is_available,
        page=page,
        page_size=page_size,
    )

    return ProductListResponse(
        products=[ProductResponse.from_product(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> ProductResponse:
    """Get a product by ID."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    product = await ProductService.get_product_by_id(
        session, UUID(product_id), organization=organization
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse.from_product(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    request: ProductUpdate,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> ProductResponse:
    """Update a product."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    product = await ProductService.get_product_by_id(
        session, UUID(product_id), organization=organization
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check slug uniqueness if changing
    if request.slug and request.slug != product.slug:
        existing = await ProductService.get_product_by_slug(session, request.slug, organization)
        if existing:
            raise HTTPException(status_code=400, detail="Product with this slug already exists")

    # Convert category_ids to UUIDs
    category_ids = (
        [UUID(cid) for cid in request.category_ids] if request.category_ids is not None else None
    )

    product = await ProductService.update_product(
        session,
        product,
        name=request.name,
        slug=request.slug,
        description=request.description,
        price_cents=request.price_cents,
        currency=request.currency,
        image_urls=request.image_urls,
        stock_available=request.stock_available,
        is_available=request.is_available,
        is_digital=request.is_digital,
        category_ids=category_ids,
    )

    return ProductResponse.from_product(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: str,
    auth_subject: CurrentUser,
    session: AsyncSession = get_db_session,
) -> None:
    """Delete a product."""
    user = auth_subject.subject
    organization = await get_user_organization(session, user)

    product = await ProductService.get_product_by_id(
        session, UUID(product_id), organization=organization
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await ProductService.delete_product(session, product)
