"""Statistics endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from timekpr_app.auth import verify_admin
from timekpr_app.models import UserStats
from timekpr_app.timekpr import get_timekpr_interface

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/users", response_model=list[str])
async def get_users(admin: str = Depends(verify_admin)) -> list[str]:
    """Get list of users managed by timekpr."""
    try:
        interface = get_timekpr_interface()
        users = interface.get_user_list()
        # Filter out system users, keep only restricted users (e.g., "agnes")
        return [u for u in users if u not in ["root", "USER"]]
    except Exception as e:
        logger.error(f"Failed to get user list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users",
        )


@router.get("/users/{username}", response_model=UserStats)
async def get_user_stats(username: str, admin: str = Depends(verify_admin)) -> UserStats:
    """Get screen time statistics for a user."""
    try:
        interface = get_timekpr_interface()
        time_left = interface.get_time_left(username)
        config = interface.get_user_config(username)
        
        # Parse config to extract limits
        daily_limit = config.get("LIMITS_PER_WEEKDAYS", [86400] * 7)
        weekly_limit = config.get("LIMIT_PER_WEEK", 604800)
        monthly_limit = config.get("LIMIT_PER_MONTH", 2678400)
        
        # Handle dbus array conversion
        if isinstance(daily_limit, (list, tuple)):
            daily_limit = daily_limit[0] if daily_limit else 86400
        else:
            daily_limit = int(daily_limit)
        
        return UserStats(
            username=username,
            time_left_today=time_left.get("day", 0),
            time_left_week=time_left.get("week", 0),
            time_left_month=time_left.get("month", 0),
            daily_limit=daily_limit,
            weekly_limit=int(weekly_limit),
            monthly_limit=int(monthly_limit),
            allowed_hours=list(range(0, 24)),  # TODO: parse from config
            allowed_weekdays=[1, 2, 3, 4, 5, 6, 7],  # TODO: parse from config
        )
    except Exception as e:
        logger.error(f"Failed to get stats for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats for {username}",
        )
