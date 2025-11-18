"""API router aggregation."""

from fastapi import APIRouter

from freely.auth import endpoints as auth_endpoints
from freely.chat import endpoints as chat_endpoints

# Main API router (all routes under /v1)
router = APIRouter(prefix="/v1")

# Include module routers
router.include_router(auth_endpoints.router)
router.include_router(chat_endpoints.router)

# TODO: Add more module routers here
# router.include_router(user_router)
# router.include_router(organization_router)
# router.include_router(product_router)

__all__ = ["router"]
