"""Authentication endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status

from timekpr_app.api.limiter import limiter
from timekpr_app.auth import create_access_token, verify_password
from timekpr_app.config import get_settings
from timekpr_app.models import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest) -> TokenResponse:
    """Login with admin password to get JWT token.
    
    Rate limited to 5 attempts per minute per IP address.
    """
    # Check password
    if not verify_password(login_data.password, settings.admin_password_hash):
        logger.warning("Failed login attempt with incorrect password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # Create token with admin username from config (not hardcoded)
    token = create_access_token(subject=settings.admin_username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
    )
