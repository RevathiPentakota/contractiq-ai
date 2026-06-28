"""Health-check router – GET /api/v1/health."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """Return the current health status of the API."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service="ContractIQ AI API",
        version=settings.app_version,
    )
