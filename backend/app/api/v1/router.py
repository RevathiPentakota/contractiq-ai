"""v1 API router – aggregates all versioned endpoint routers."""

from fastapi import APIRouter

from app.api.v1 import health, contracts

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(contracts.router, prefix="/contracts")
