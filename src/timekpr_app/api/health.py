"""Health and status endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from timekpr_app import __version__
from timekpr_app.config import get_settings
from timekpr_app.models import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version=__version__,
        environment=settings.app_env,
    )
