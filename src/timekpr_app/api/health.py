"""Health and status endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Request

from timekpr_app import __version__
from timekpr_app.api.limiter import limiter
from timekpr_app.config import get_settings
from timekpr_app.models import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get("", response_model=HealthResponse)
@limiter.limit("60/minute")
async def health_check(request: Request) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version=__version__,
        environment=settings.app_env,
    )
