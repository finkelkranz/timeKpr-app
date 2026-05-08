"""Statistics endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from timekpr_app.auth import verify_admin
from timekpr_app.models import UserStats
from timekpr_app.timekpr import get_timekpr_interface
from timekpr_app.timekpr_file import get_all_users_data, get_user_data, add_time_to_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/users", response_model=list[str])
async def get_users(admin: str = Depends(verify_admin)) -> list[str]:
    """Get list of users managed by timekpr.
    
    Uses file-based reading from /var/lib/timekpr/config/ for reliability.
    Falls back to D-Bus if file reading fails.
    """
    try:
        # Try file-based reading first (most reliable for real data)
        try:
            users_data = get_all_users_data()
            users = [u.username for u in users_data]
            if users:
                logger.info(f"Got {len(users)} users from files")
                return users
        except Exception as e:
            logger.warning(f"File-based user list failed: {e}, falling back to D-Bus")
        
        # Fallback to D-Bus
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
    """Get screen time statistics for a user.
    
    Uses file-based reading from /var/lib/timekpr/ for actual consumed time.
    Falls back to D-Bus interface if file reading fails.
    """
    try:
        # Try file-based reading first (most reliable for real data including consumed time)
        user_data = None
        try:
            user_data = get_user_data(username)
        except Exception as e:
            logger.warning(f"File-based reading failed for {username}: {e}, falling back to D-Bus")
        
        if user_data:
            # Convert file-based data to UserStats model
            # Flatten allowed hours from all days
            all_hours = set()
            for day_hours in user_data.limits.allowed_hours.values():
                all_hours.update(day_hours)
            
            return UserStats(
                username=username,
                time_left_today=user_data.remaining_day,
                time_left_week=user_data.remaining_week,
                time_left_month=user_data.remaining_month,
                daily_limit=user_data.limits.daily,
                weekly_limit=user_data.limits.weekly,
                monthly_limit=user_data.limits.monthly,
                allowed_hours=sorted(all_hours),
                allowed_weekdays=user_data.limits.allowed_weekdays,
            )
        
        # Fallback to D-Bus interface (won't have consumed time, only limits)
        interface = get_timekpr_interface()
        time_left = interface.get_time_left(username)
        config = interface.get_user_config(username)
        
        # Parse config to extract limits - use defaults if empty
        if config:
            daily_limit = config.get("LIMITS_PER_WEEKDAYS", config.get("LIMIT_PER_WEEKDAY", 14400))
            weekly_limit = config.get("LIMIT_PER_WEEK", 100800)
            monthly_limit = config.get("LIMIT_PER_MONTH", 504000)
        else:
            daily_limit = 14400
            weekly_limit = 100800
            monthly_limit = 504000
        
        # Handle dbus array conversion
        if isinstance(daily_limit, (list, tuple)):
            daily_limit = daily_limit[0] if daily_limit else 14400
        else:
            daily_limit = int(daily_limit)
        
        if isinstance(weekly_limit, (list, tuple)):
            weekly_limit = weekly_limit[0] if weekly_limit else 100800
        else:
            weekly_limit = int(weekly_limit)
        
        if isinstance(monthly_limit, (list, tuple)):
            monthly_limit = monthly_limit[0] if monthly_limit else 504000
        else:
            monthly_limit = int(monthly_limit)
        
        # Parse allowed days (1-7)
        allowed_weekdays = config.get("ALLOWED_DAYS", [1, 2, 3, 4, 5]) if config else [1, 2, 3, 4, 5]
        if isinstance(allowed_weekdays, (list, tuple)):
            allowed_weekdays = list(allowed_weekdays)
        
        # Parse allowed hours per day - flatten all hours from all days
        allowed_hours_raw = config.get("ALLOWED_HOURS", {}) if config else {}
        if isinstance(allowed_hours_raw, dict):
            all_hours = set()
            for day_hours in allowed_hours_raw.values():
                if isinstance(day_hours, (list, tuple)):
                    all_hours.update(day_hours)
            allowed_hours = sorted(all_hours)
        elif isinstance(allowed_hours_raw, (list, tuple)):
            allowed_hours = sorted(set(allowed_hours_raw))
        else:
            allowed_hours = list(range(0, 24))
        
        return UserStats(
            username=username,
            time_left_today=time_left.get("day", 0),
            time_left_week=time_left.get("week", 0),
            time_left_month=time_left.get("month", 0),
            daily_limit=daily_limit,
            weekly_limit=weekly_limit,
            monthly_limit=monthly_limit,
            allowed_hours=allowed_hours,
            allowed_weekdays=allowed_weekdays,
        )
    except Exception as e:
        logger.error(f"Failed to get stats for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats for {username}",
        )


@router.post("/users/{username}/add-time")
async def add_time_to_user_endpoint(
    username: str,
    seconds: int,
    period: str = "day",
    admin: str = Depends(verify_admin),
) -> dict[str, Any]:
    """Add time to a user's remaining time.
    
    This is the primary endpoint for the use case:
    "Parent opens app on mobile and gives child more time to finish homework"
    
    Args:
        username: The username to add time for
        seconds: Number of seconds to ADD (e.g., 3600 = 1 hour)
        period: "day", "week", or "month" - which time period to extend
        
    Returns:
        Success message with new remaining time
        
    Example:
        POST /api/stats/users/agnes/add-time
        {"seconds": 3600, "period": "day"}
        
        Adds 1 hour to Agnes's remaining daily time.
    """
    if period not in ("day", "week", "month"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be 'day', 'week', or 'month'",
        )
    
    if seconds <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seconds must be a positive number",
        )
    
    try:
        # First get current state to return in response
        user_data = get_user_data(username)
        
        # Add the time via D-Bus
        success = add_time_to_user(username, seconds, period)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add {seconds}s to {username}'s {period} time",
            )
        
        # Get updated state
        user_data_after = get_user_data(username)
        
        # Return success with time info
        remaining_key = f"remaining_{period}"
        remaining_before = getattr(user_data, remaining_key, 0) if user_data else 0
        remaining_after = getattr(user_data_after, remaining_key, 0) if user_data_after else remaining_before + seconds
        
        return {
            "status": "ok",
            "message": f"Added {seconds}s to {username}'s {period} time",
            "user": username,
            "period": period,
            "seconds_added": seconds,
            "remaining_before": remaining_before,
            "remaining_after": remaining_after,
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found in timekpr",
        )
    except Exception as e:
        logger.error(f"Failed to add time for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add time: {e}",
        )
