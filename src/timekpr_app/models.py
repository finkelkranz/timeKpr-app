"""Pydantic models for API requests/responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request model."""

    password: str = Field(..., min_length=1, description="Admin password")


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserStats(BaseModel):
    """User screen time statistics."""

    username: str
    time_left_today: int  # seconds
    time_left_week: int  # seconds
    time_left_month: int  # seconds
    daily_limit: int  # seconds
    weekly_limit: int  # seconds
    monthly_limit: int  # seconds
    allowed_hours: list[int]  # 0-23
    allowed_weekdays: list[int]  # 1-7 (Monday=1, Sunday=7)


class UserConfig(BaseModel):
    """User configuration."""

    username: str
    daily_limit: int  # seconds
    weekly_limit: int  # seconds
    monthly_limit: int  # seconds
    allowed_hours: list[int]  # 0-23 for each day
    allowed_weekdays: list[int]  # 1-7
    track_inactive: bool
    hide_tray_icon: bool
    lockout_type: str  # lock, suspend, suspendwake, terminate, shutdown


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str
    environment: str
