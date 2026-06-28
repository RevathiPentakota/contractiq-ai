"""v1 API router – aggregates all versioned endpoint routers."""

from fastapi import APIRouter

from app.api.v1 import health

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)

# Future feature routers are registered here:
# from app.api.v1 import contracts, users
# router.include_router(contracts.router, prefix="/contracts")
# router.include_router(users.router, prefix="/users")
