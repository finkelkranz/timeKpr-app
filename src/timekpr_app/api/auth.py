"""Authentication endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from timekpr_app.auth import create_access_token, verify_password
from timekpr_app.config import get_settings
from timekpr_app.models import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """Login with admin password to get JWT token."""
    # Check password
    if not verify_password(request.password, settings.admin_password_hash):
        logger.warning("Failed login attempt with incorrect password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Create token
    token = create_access_token(subject="admin")
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
    )
