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
        
        return UserConfig(
            username=username,
            daily_limit=86400,  # TODO: parse from config
            weekly_limit=604800,
            monthly_limit=2678400,
            allowed_hours=list(range(0, 24)),
            allowed_weekdays=[1, 2, 3, 4, 5, 6, 7],
            track_inactive=False,
            hide_tray_icon=False,
            lockout_type="terminate",
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
