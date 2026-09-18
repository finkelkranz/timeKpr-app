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


class AddTimeRequest(BaseModel):
    """Request model for adding time to a user."""

    seconds: int = Field(..., gt=0, description="Number of seconds to add")
    period: str = Field(default="day", description="Time period: day, week, or month")


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


# --- Configuration Request Models ---


class SetTimeLeftRequest(BaseModel):
    """Request model for setting remaining time for today."""

    seconds: int = Field(..., ge=0, description="Number of seconds remaining for today")


class SetAllowedHoursRequest(BaseModel):
    """Request model for setting allowed hours for a day."""

    day: int = Field(..., ge=1, le=7, description="Day of week (1=Monday, 7=Sunday)")
    hours: list[int] = Field(
        ..., min_length=1, description="List of allowed hours (0-23)"
    )


# --- Statistics History Query Models ---


class UserHistoryQuery(BaseModel):
    """Query parameters for user history endpoint."""

    days: int = Field(
        default=7, ge=1, le=365, description="Number of days of history"
    )


class DailyUsageQuery(BaseModel):
    """Query parameters for daily usage endpoint."""

    date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date in YYYY-MM-DD format",
    )


class LeaderboardQuery(BaseModel):
    """Query parameters for leaderboard endpoint."""

    limit: int = Field(
        default=10, ge=1, le=100, description="Maximum number of users"
    )
    days: int = Field(
        default=7, ge=1, le=365, description="Number of days to consider"
    )
