"""Authentication and JWT token handling."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from timekpr_app.config import get_settings

logger = logging.getLogger(__name__)

security = HTTPBearer()
settings = get_settings()


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create JWT token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    """Get current user from JWT token."""
    token = credentials.credentials
    return verify_token(token)


async def verify_admin(current_user: dict[str, Any] = Depends(get_current_user)) -> str:
    """Verify that current user is admin."""
    # In this setup, we only have one admin user ("admin")
    if current_user.get("sub") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return "admin"
