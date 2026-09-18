"""Statistics history endpoints for timekpr.

This module provides API endpoints for retrieving historical
statistics data from the SQLite database.

Endpoints:
- GET /stats-history/users/{username} - Get history for a user
- GET /stats-history/users/{username}/daily - Get daily usage
- GET /stats-history/leaderboard - Get leaderboard of most active users
- GET /stats-history/users/{username}/weekly - Get weekly summary
"""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from timekpr_app.api.limiter import limiter
from timekpr_app.auth import verify_admin
from timekpr_app.timekpr_db import (
    DB_FILE,
    get_daily_usage,
    get_leaderboard,
    get_user_history,
    get_weekly_summary,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats-history", tags=["statistics-history"])


def _validate_date_format(date: str | None) -> str | None:
    """Validate date format YYYY-MM-DD."""
    if date is None:
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date must be in YYYY-MM-DD format",
        )
    return date


@router.get("/users/{username}")
@limiter.limit("20/minute")
async def get_user_history_endpoint(
    request: Request,
    username: str,
    days: int = Query(default=7, ge=1, le=365, description="Number of days of history"),
    admin: str = Depends(verify_admin),
) -> list[dict[str, Any]]:
    """Get historical statistics for a specific user.
    
    Returns time series data showing how much time the user has spent
    over the specified period.
    
    Example response:
    [
        {
            "id": 1,
            "username": "agnes",
            "timestamp": "2024-01-15T10:30:00",
            "time_spent_day": 1800,
            "time_spent_week": 5400,
            "remaining_day": 12600,
            "daily_limit": 14400,
            ...
        },
        ...
    ]
    """
    try:
        history = get_user_history(username, days)
        return history
    except Exception as e:
        logger.error(f"Failed to get history for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history for {username}",
        ) from None


@router.get("/users/{username}/daily")
@limiter.limit("20/minute")
async def get_daily_usage_endpoint(
    request: Request,
    username: str,
    date: str | None = Query(
        default=None, description="Date in YYYY-MM-DD format. Defaults to today."
    ),
    admin: str = Depends(verify_admin),
) -> list[dict[str, Any]]:
    """Get daily usage statistics for a user.
    
    Returns all snapshots taken for the specified day.
    
    Example:
        GET /api/stats-history/users/agnes/daily?date=2024-01-15
    """
    try:
        # Validate date format
        if date:
            _validate_date_format(date)
        usage = get_daily_usage(username, date)
        return usage
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get daily usage for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch daily usage for {username}",
        ) from None


@router.get("/users/{username}/weekly")
@limiter.limit("20/minute")
async def get_weekly_summary_endpoint(
    request: Request,
    username: str,
    admin: str = Depends(verify_admin),
) -> dict[str, Any]:
    """Get weekly summary for a user.
    
    Returns aggregated statistics for the current week,
    showing total time spent and comparison with limits.
    
    Example response:
    {
        "username": "agnes",
        "period": "week",
        "start_time": "2024-01-15T00:00:00",
        "end_time": "2024-01-22T10:30:00",
        "time_spent": 18000,
        "time_spent_hours": 5.0
    }
    """
    try:
        summary = get_weekly_summary(username)
        if "error" in summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=summary["error"],
            )
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get weekly summary for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch weekly summary for {username}",
        ) from None


@router.get("/leaderboard")
@limiter.limit("15/minute")
async def get_leaderboard_endpoint(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of users"),
    days: int = Query(default=7, ge=1, le=365, description="Number of days to consider"),
    admin: str = Depends(verify_admin),
) -> list[dict[str, Any]]:
    """Get leaderboard of most active users.
    
    Returns users sorted by total time spent (descending).
    Useful for seeing which users are most active.
    
    Example response:
    [
        {
            "username": "agnes",
            "max_daily": 14400,
            "avg_daily": 7200,
            "total_spent": 50400,
            "readings": 24
        },
        {
            "username": "torgeir",
            ...
        }
    ]
    """
    try:
        leaderboard = get_leaderboard(limit, days)
        return leaderboard
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leaderboard",
        ) from None


@router.get("/info")
async def get_db_info(
    admin: str = Depends(verify_admin),
) -> dict[str, Any]:
    """Get database information and statistics.
    
    Returns metadata about the statistics database.
    """
    import os
    
    try:
        db_path = DB_FILE
        
        # Check if database exists
        exists = os.path.exists(str(db_path))
        
        # Get file size
        size = 0
        if exists:
            size = os.path.getsize(str(db_path))
        
        # Count records
        from timekpr_app.timekpr_db import get_db
        record_count = 0
        if exists:
            try:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM user_stats_history")
                    record_count = cursor.fetchone()[0]
            except Exception:
                record_count = 0
        
        return {
            "database_path": str(db_path),
            "exists": exists,
            "size_bytes": size,
            "size_mb": round(size / (1024 * 1024), 2),
            "record_count": record_count,
        }
    except Exception as e:
        logger.error(f"Failed to get DB info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch database info",
        ) from None
