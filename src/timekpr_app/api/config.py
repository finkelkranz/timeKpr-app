"""User configuration endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from timekpr_app.auth import verify_admin
from timekpr_app.models import UserConfig
from timekpr_app.timekpr import get_timekpr_interface

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/config", tags=["configuration"])


@router.get("/users/{username}", response_model=UserConfig)
async def get_user_config(
    username: str, admin: str = Depends(verify_admin)
) -> UserConfig:
    """Get user's complete timekpr configuration."""
    try:
        interface = get_timekpr_interface()
        config = interface.get_user_config(username)
        
        # Parse limits from config with defaults
        daily_limit = config.get("LIMITS_PER_WEEKDAYS", config.get("LIMIT_PER_WEEKDAY", 14400))
        weekly_limit = config.get("LIMIT_PER_WEEK", 100800)
        monthly_limit = config.get("LIMIT_PER_MONTH", 504000)
        
        # Handle dbus array types - extract first element if array
        if isinstance(daily_limit, (list, tuple)) and daily_limit:
            daily_limit = daily_limit[0]
        if isinstance(weekly_limit, (list, tuple)) and weekly_limit:
            weekly_limit = weekly_limit[0]
        if isinstance(monthly_limit, (list, tuple)) and monthly_limit:
            monthly_limit = monthly_limit[0]
        
        # Parse allowed days (1-7)
        allowed_weekdays = config.get("ALLOWED_DAYS", [1, 2, 3, 4, 5])
        if isinstance(allowed_weekdays, (list, tuple)):
            allowed_weekdays = list(allowed_weekdays)
        
        # Parse allowed hours per day - flatten all hours from all days
        # Config may have ALLOWED_HOURS as dict {day: [hours]} or list
        allowed_hours_raw = config.get("ALLOWED_HOURS", {})
        if isinstance(allowed_hours_raw, dict):
            # Extract all unique hours across all days
            all_hours = set()
            for day_hours in allowed_hours_raw.values():
                if isinstance(day_hours, (list, tuple)):
                    all_hours.update(day_hours)
            allowed_hours = sorted(all_hours)
        elif isinstance(allowed_hours_raw, (list, tuple)):
            allowed_hours = sorted(set(allowed_hours_raw))
        else:
            allowed_hours = list(range(0, 24))
        
        # Parse boolean/tracking settings
        track_inactive = config.get("TRACK_INACTIVE", False)
        hide_tray_icon = config.get("HIDE_TRAY_ICON", False)
        lockout_type = config.get("LOCKOUT_TYPE", "terminate")
        
        # Convert to proper types
        return UserConfig(
            username=username,
            daily_limit=int(daily_limit),
            weekly_limit=int(weekly_limit),
            monthly_limit=int(monthly_limit),
            allowed_hours=allowed_hours,
            allowed_weekdays=allowed_weekdays,
            track_inactive=bool(track_inactive) if track_inactive else False,
            hide_tray_icon=bool(hide_tray_icon) if hide_tray_icon else False,
            lockout_type=str(lockout_type),
        )
    except Exception as e:
        logger.error(f"Failed to get config for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch config for {username}",
        )


@router.put("/users/{username}/time-left-today")
async def set_time_left_today(
    username: str,
    seconds: int,
    admin: str = Depends(verify_admin),
) -> dict[str, str]:
    """Adjust remaining time for today."""
    try:
        interface = get_timekpr_interface()
        success = interface.set_time_left_day(username, seconds)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set time for {username}",
            )
        
        return {"status": "ok", "message": f"Set daily time to {seconds}s for {username}"}
    except Exception as e:
        logger.error(f"Failed to set time for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set time for {username}",
        )


@router.put("/users/{username}/allowed-hours")
async def set_allowed_hours(
    username: str,
    day: int,
    hours: list[int],
    admin: str = Depends(verify_admin),
) -> dict[str, str]:
    """Set allowed hours for a specific day (1-7)."""
    if day < 1 or day > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Day must be between 1 and 7",
        )
    
    try:
        interface = get_timekpr_interface()
        success = interface.set_allowed_hours(username, day, hours)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set hours for {username}",
            )
        
        return {"status": "ok", "message": f"Updated allowed hours for {username}"}
    except Exception as e:
        logger.error(f"Failed to set hours for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set hours for {username}",
        )
