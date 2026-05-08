"""Mock D-Bus interface for testing without affecting real timekpr users.

This mock implementation returns realistic data and logs all operations
without making actual D-Bus calls. Useful for:
- Unit testing
- CI/CD pipelines
- Development without risking real users
"""

from __future__ import annotations

import logging
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Mock user database - safe for testing
MOCK_USERS = {
    "testuser": {
        "display_name": "Test User",
        "daily_limit": 14400,      # 4 hours
        "weekly_limit": 100800,    # 28 hours
        "monthly_limit": 504000,   # 140 hours
        "allowed_days": [1, 2, 3, 4, 5],  # Mon-Fri
        "allowed_hours": {
            1: list(range(8, 18)),   # Mon: 8am-6pm
            2: list(range(8, 18)),   # Tue: 8am-6pm
            3: list(range(8, 18)),   # Wed: 8am-6pm
            4: list(range(8, 18)),   # Thu: 8am-6pm
            5: list(range(8, 18)),   # Fri: 8am-6pm
            6: list(range(10, 18)),  # Sat: 10am-6pm
            7: list(range(10, 18)),  # Sun: 10am-6pm
        },
        "time_left_day": 10800,     # 3 hours remaining today
        "time_left_week": 50400,    # 14 hours remaining this week
        "time_left_month": 302400,  # 84 hours remaining this month
        "track_inactive": False,
        "hide_tray_icon": False,
        "lockout_type": "terminate",
        "playtime_enabled": False,
    }
}

# Track all operations for debugging
OPERATION_LOG: list[dict[str, Any]] = []


class MockTimekprDBusInterface:
    """Mock wrapper for testing - doesn't affect real timekpr."""

    def __init__(self) -> None:
        """Initialize mock interface."""
        logger.info("MockTimekprDBusInterface initialized (NOT using real D-Bus)")

    def _log_operation(self, op_type: str, method: str, **kwargs: Any) -> None:
        """Log an operation for debugging."""
        OPERATION_LOG.append({
            "timestamp": datetime.now().isoformat(),
            "type": op_type,
            "method": method,
            **kwargs,
        })
        logger.debug(f"Mock operation: {op_type} {method} {kwargs}")

    def get_user_list(self) -> list[str]:
        """Get list of mock test users."""
        self._log_operation("read", "get_user_list")
        users = list(MOCK_USERS.keys())
        logger.info(f"Mock: Found {len(users)} users: {users}")
        return users

    def get_user_config(self, username: str) -> dict[str, Any]:
        """Get mock user configuration."""
        self._log_operation("read", "get_user_config", username=username)
        
        if username not in MOCK_USERS:
            logger.warning(f"Mock: User '{username}' not found")
            return {}
        
        user_data = MOCK_USERS[username]
        config = {
            "LIMITS_PER_WEEKDAYS": user_data["daily_limit"],
            "LIMIT_PER_WEEK": user_data["weekly_limit"],
            "LIMIT_PER_MONTH": user_data["monthly_limit"],
            "ALLOWED_DAYS": user_data["allowed_days"],
            "ALLOWED_HOURS": user_data["allowed_hours"],
            "TRACK_INACTIVE": user_data["track_inactive"],
            "HIDE_TRAY_ICON": user_data["hide_tray_icon"],
            "LOCKOUT_TYPE": user_data["lockout_type"],
        }
        logger.info(f"Mock: Returned config for '{username}' with {len(config)} keys")
        return config

    def get_time_left(self, username: str) -> dict[str, int]:
        """Get mock remaining time for user."""
        self._log_operation("read", "get_time_left", username=username)
        
        if username not in MOCK_USERS:
            logger.warning(f"Mock: User '{username}' not found")
            return {"day": 0, "week": 0, "month": 0}
        
        user_data = MOCK_USERS[username]
        result = {
            "day": user_data["time_left_day"],
            "week": user_data["time_left_week"],
            "month": user_data["time_left_month"],
        }
        logger.info(f"Mock: Returned time_left for '{username}': {result}")
        return result

    def get_time_limits(self, username: str) -> dict[str, Any]:
        """Get mock time limits."""
        self._log_operation("read", "get_time_limits", username=username)
        
        if username not in MOCK_USERS:
            return {}
        
        user_data = MOCK_USERS[username]
        return {
            "daily": user_data["daily_limit"],
            "weekly": user_data["weekly_limit"],
            "monthly": user_data["monthly_limit"],
        }

    def set_time_left_day(self, username: str, seconds: int) -> bool:
        """Mock: Set remaining time for today."""
        self._log_operation("write", "set_time_left_day", username=username, seconds=seconds)
        
        if username not in MOCK_USERS:
            logger.error(f"Mock: User '{username}' not found")
            return False
        
        MOCK_USERS[username]["time_left_day"] = seconds
        logger.info(f"Mock: Set daily time for '{username}' to {seconds}s")
        return True

    def set_time_left_week(self, username: str, seconds: int) -> bool:
        """Mock: Set remaining time for this week."""
        self._log_operation("write", "set_time_left_week", username=username, seconds=seconds)
        
        if username not in MOCK_USERS:
            return False
        
        MOCK_USERS[username]["time_left_week"] = seconds
        logger.info(f"Mock: Set weekly time for '{username}' to {seconds}s")
        return True

    def set_time_left_month(self, username: str, seconds: int) -> bool:
        """Mock: Set remaining time for this month."""
        self._log_operation("write", "set_time_left_month", username=username, seconds=seconds)
        
        if username not in MOCK_USERS:
            return False
        
        MOCK_USERS[username]["time_left_month"] = seconds
        logger.info(f"Mock: Set monthly time for '{username}' to {seconds}s")
        return True

    def set_allowed_hours(self, username: str, day: int, hours: list[int]) -> bool:
        """Mock: Set allowed hours for specific day (1=Monday, 7=Sunday).
        
        Args:
            username: Username
            day: Day of week (1-7)
            hours: List of allowed hours (0-23)
        """
        self._log_operation("write", "set_allowed_hours", username=username, day=day, hours=hours)
        
        if username not in MOCK_USERS:
            logger.error(f"Mock: User '{username}' not found")
            return False
        
        if day < 1 or day > 7:
            logger.error(f"Mock: Invalid day {day} (must be 1-7)")
            return False
        
        MOCK_USERS[username]["allowed_hours"][day] = sorted(set(hours))
        logger.info(f"Mock: Set allowed hours for '{username}' on day {day}: {hours}")
        return True

    def set_allowed_days(self, username: str, days: list[int]) -> bool:
        """Mock: Set allowed weekdays (1=Monday, 7=Sunday)."""
        self._log_operation("write", "set_allowed_days", username=username, days=days)
        
        if username not in MOCK_USERS:
            logger.error(f"Mock: User '{username}' not found")
            return False
        
        # Validate days
        for day in days:
            if day < 1 or day > 7:
                logger.error(f"Mock: Invalid day {day} (must be 1-7)")
                return False
        
        MOCK_USERS[username]["allowed_days"] = sorted(set(days))
        logger.info(f"Mock: Set allowed days for '{username}': {days}")
        return True

    def set_limits_per_weekday(self, username: str, day_limits: dict[int, int]) -> bool:
        """Mock: Set daily limits for each weekday in seconds."""
        self._log_operation("write", "set_limits_per_weekday", username=username, day_limits=day_limits)
        
        if username not in MOCK_USERS:
            return False
        
        for day in range(1, 8):
            if day in day_limits:
                MOCK_USERS[username]["daily_limit"] = day_limits[day]
        
        logger.info(f"Mock: Set daily limits for '{username}': {day_limits}")
        return True

    def set_limit_week(self, username: str, seconds: int) -> bool:
        """Mock: Set weekly limit in seconds."""
        self._log_operation("write", "set_limit_week", username=username, seconds=seconds)
        
        if username not in MOCK_USERS:
            return False
        
        MOCK_USERS[username]["weekly_limit"] = seconds
        logger.info(f"Mock: Set weekly limit for '{username}' to {seconds}s")
        return True

    def set_limit_month(self, username: str, seconds: int) -> bool:
        """Mock: Set monthly limit in seconds."""
        self._log_operation("write", "set_limit_month", username=username, seconds=seconds)
        
        if username not in MOCK_USERS:
            return False
        
        MOCK_USERS[username]["monthly_limit"] = seconds
        logger.info(f"Mock: Set monthly limit for '{username}' to {seconds}s")
        return True


def get_operation_log() -> list[dict[str, Any]]:
    """Get all logged operations for debugging/testing."""
    return OPERATION_LOG.copy()


def clear_operation_log() -> None:
    """Clear operation log."""
    OPERATION_LOG.clear()


def get_mock_user_state(username: str) -> dict[str, Any] | None:
    """Get current state of a mock user (for assertions in tests)."""
    return MOCK_USERS.get(username)


def reset_mock_users() -> None:
    """Reset mock users to initial state."""
    global MOCK_USERS
    MOCK_USERS = {
        "testuser": {
            "display_name": "Test User",
            "daily_limit": 14400,
            "weekly_limit": 100800,
            "monthly_limit": 504000,
            "allowed_days": [1, 2, 3, 4, 5],
            "allowed_hours": {
                1: list(range(8, 18)),
                2: list(range(8, 18)),
                3: list(range(8, 18)),
                4: list(range(8, 18)),
                5: list(range(8, 18)),
                6: list(range(10, 18)),
                7: list(range(10, 18)),
            },
            "time_left_day": 10800,
            "time_left_week": 50400,
            "time_left_month": 302400,
            "track_inactive": False,
            "hide_tray_icon": False,
            "lockout_type": "terminate",
            "playtime_enabled": False,
        }
    }
    OPERATION_LOG.clear()
    logger.info("Mock users reset to initial state")
