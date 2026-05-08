"""File-based reader for timekpr data.

This module reads timekpr configuration and usage data directly from files
under /var/lib/timekpr/. This is the most reliable way to get actual
consumed time, as timekpr sends this via D-Bus signals which are hard to
capture in a web application context.

Files:
- Config: /var/lib/timekpr/config/timekpr.{username}.conf
- Usage:  /var/lib/timekpr/work/{username}.time

Requires root access to read these files.
"""

from __future__ import annotations

import glob
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# Default paths
TIMEKPR_CONFIG_DIR = "/var/lib/timekpr/config"
TIMEKPR_WORK_DIR = "/var/lib/timekpr/work"


@dataclass
class TimekprUserLimits:
    """Time limits for a user."""
    daily: int = 0        # Seconds per weekday (using first weekday)
    weekly: int = 0       # Seconds per week
    monthly: int = 0      # Seconds per month
    allowed_weekdays: list[int] = None  # Days 1-7 (Mon-Sun)
    allowed_hours: dict[int, list[int]] = None  # {day: [hours]}
    lockout_type: str = "terminate"
    track_inactive: bool = False
    hide_tray_icon: bool = False

    def __post_init__(self):
        if self.allowed_weekdays is None:
            self.allowed_weekdays = []
        if self.allowed_hours is None:
            self.allowed_hours = {}


@dataclass
class TimekprUserUsage:
    """Time usage/consumed for a user."""
    day: int = 0          # Seconds spent today
    week: int = 0         # Seconds spent this week
    month: int = 0        # Seconds spent this month
    balance_day: int = 0   # Balance for today
    last_checked: str = "" # Timestamp of last update


@dataclass
class TimekprUserData:
    """Complete timekpr data for a user."""
    username: str
    limits: TimekprUserLimits
    usage: TimekprUserUsage
    display_name: str = ""

    @property
    def remaining_day(self) -> int:
        """Remaining time today in seconds."""
        return max(0, self.limits.daily - self.usage.day)

    @property
    def remaining_week(self) -> int:
        """Remaining time this week in seconds."""
        return max(0, self.limits.weekly - self.usage.week)

    @property
    def remaining_month(self) -> int:
        """Remaining time this month in seconds."""
        return max(0, self.limits.monthly - self.usage.month)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "username": self.username,
            "display_name": self.display_name,
            "limits": {
                "daily": self.limits.daily,
                "weekly": self.limits.weekly,
                "monthly": self.limits.monthly,
                "allowed_weekdays": self.limits.allowed_weekdays,
                "allowed_hours": self.limits.allowed_hours,
                "lockout_type": self.limits.lockout_type,
                "track_inactive": self.limits.track_inactive,
                "hide_tray_icon": self.limits.hide_tray_icon,
            },
            "usage": {
                "day": self.usage.day,
                "week": self.usage.week,
                "month": self.usage.month,
                "balance_day": self.usage.balance_day,
            },
            "remaining": {
                "day": self.remaining_day,
                "week": self.remaining_week,
                "month": self.remaining_month,
            },
            "last_checked": self.usage.last_checked,
        }


def parse_config_file(filepath: str) -> TimekprUserLimits:
    """Parse a timekpr configuration file.
    
    File format: INI-like with [username] section and KEY=value pairs.
    """
    limits = TimekprUserLimits()
    
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.warning(f"Cannot read config file {filepath}: {e}")
        return limits
    
    # Parse the file manually (simple INI format)
    current_section = None
    allowed_hours = {}
    
    for line in content.split("\n"):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith("#") or line.startswith("####"):
            continue
        
        # Section header
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            # Reset allowed_hours for new user section
            if current_section and not current_section.endswith(".PLAYTIME"):
                allowed_hours = {}
            continue
        
        # Key-value pairs
        if "=" in line and current_section:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            
            # Parse limits
            if key == "LIMITS_PER_WEEKDAYS":
                # Semicolon-separated list of limits for each weekday
                values = [v.strip() for v in value.split(";") if v.strip()]
                if values:
                    limits.daily = int(values[0])  # Use first weekday (Monday)
                # Store all for reference
                limits.allowed_hours = {}
                for i, v in enumerate(values, start=1):
                    if i <= 7:
                        limits.allowed_hours[i] = int(v)
            
            elif key == "LIMIT_PER_WEEK":
                limits.weekly = int(value) if value else 0
            
            elif key == "LIMIT_PER_MONTH":
                limits.monthly = int(value) if value else 0
            
            elif key == "ALLOWED_WEEKDAYS":
                limits.allowed_weekdays = [int(v) for v in value.split(";") if v.strip()]
            
            elif key.startswith("ALLOWED_HOURS_"):
                # ALLOWED_HOURS_1 = 8;9;10;11
                day_str = key.replace("ALLOWED_HOURS_", "")
                try:
                    day = int(day_str)
                    if 1 <= day <= 7:
                        hours = [int(v) for v in value.split(";") if v.strip()]
                        allowed_hours[day] = hours
                        # Also store in limits for backward compatibility
                        if not hasattr(limits, '_raw_allowed_hours'):
                            limits._raw_allowed_hours = {}
                        limits._raw_allowed_hours[day] = hours
                except ValueError:
                    pass
            
            elif key == "LOCKOUT_TYPE":
                limits.lockout_type = value
            
            elif key == "TRACK_INACTIVE":
                limits.track_inactive = value.lower() in ("true", "1", "yes")
            
            elif key == "HIDE_TRAY_ICON":
                limits.hide_tray_icon = value.lower() in ("true", "1", "yes")
    
    # Store parsed allowed_hours
    limits.allowed_hours = allowed_hours
    
    return limits


def parse_work_file(filepath: str) -> TimekprUserUsage:
    """Parse a timekpr work/usage file.
    
    File format: INI-like with [username] section.
    """
    usage = TimekprUserUsage()
    
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.warning(f"Cannot read work file {filepath}: {e}")
        return usage
    
    current_section = None
    
    for line in content.split("\n"):
        line = line.strip()
        
        if not line or line.startswith("#") or line.startswith("####"):
            continue
        
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            continue
        
        if "=" in line and current_section:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            
            if key == "TIME_SPENT_DAY":
                usage.day = int(value) if value else 0
            elif key == "TIME_SPENT_WEEK":
                usage.week = int(value) if value else 0
            elif key == "TIME_SPENT_MONTH":
                usage.month = int(value) if value else 0
            elif key == "TIME_SPENT_BALANCE":
                usage.balance_day = int(value) if value else 0
            elif key == "LAST_CHECKED":
                usage.last_checked = value
    
    return usage


def get_timekpr_users() -> list[str]:
    """Get list of all configured timekpr users from config directory."""
    users = []
    
    if not os.path.isdir(TIMEKPR_CONFIG_DIR):
        logger.warning(f"Config directory not found: {TIMEKPR_CONFIG_DIR}")
        return users
    
    # Find all config files: timekpr.{username}.conf
    pattern = os.path.join(TIMEKPR_CONFIG_DIR, "timekpr.*.conf")
    
    for filepath in glob.glob(pattern):
        # Extract username from filename: timekpr.agnes.conf -> agnes
        basename = os.path.basename(filepath)
        if basename.startswith("timekpr.") and basename.endswith(".conf"):
            # 'timekpr.' is 9 characters (t,i,m,e,k,p,r,., = 8? No, it's 9)
            # Actually: t(1) i(2) m(3) e(4) k(5) p(6) r(7) .(8) = 8 chars
            # So we need [8:-5]
            username = basename[8:-5]  # Remove 'timekpr.' prefix (8 chars) and '.conf' suffix (5 chars)
            # Skip special files
            if username and username not in ("USER", "root", "SER"):
                users.append(username)
    
    return sorted(users)


def get_user_data(username: str) -> TimekprUserData | None:
    """Get complete timekpr data for a specific user.
    
    Args:
        username: The username to get data for
        
    Returns:
        TimekprUserData object or None if user not found
    """
    # Try to find config file
    config_pattern = os.path.join(TIMEKPR_CONFIG_DIR, f"timekpr.{username}.conf")
    work_pattern = os.path.join(TIMEKPR_WORK_DIR, f"{username}.time")
    
    if not os.path.exists(config_pattern):
        logger.warning(f"Config file not found for user '{username}': {config_pattern}")
        return None
    
    limits = parse_config_file(config_pattern)
    usage = parse_work_file(work_pattern)
    
    return TimekprUserData(
        username=username,
        limits=limits,
        usage=usage,
        display_name=username,  # TODO: get display name from config
    )


def get_all_users_data() -> list[TimekprUserData]:
    """Get complete timekpr data for all configured users."""
    users = get_timekpr_users()
    results = []
    
    for username in users:
        data = get_user_data(username)
        if data:
            results.append(data)
    
    return results


def add_time_to_user(username: str, seconds: int, period: str = "day") -> bool:
    """Add time to a user's remaining time.
    
    This is a convenience function that uses the D-Bus interface to add time.
    For actual implementation, use TimekprDBusInterface.set_time_left_* methods.
    
    Args:
        username: The username
        seconds: Number of seconds to ADD (not set)
        period: "day", "week", or "month"
        
    Returns:
        True if successful, False otherwise
    """
    from timekpr_app.timekpr import get_timekpr_interface
    
    try:
        interface = get_timekpr_interface()
        
        if period == "day":
            # Use "+=" to add time (relative)
            # Note: D-Bus API uses "=" for set, but we need to calculate and set
            # Get current remaining time
            user_data = get_user_data(username)
            if user_data:
                new_time = user_data.remaining_day + seconds
                return interface.set_time_left_day(username, new_time)
        elif period == "week":
            user_data = get_user_data(username)
            if user_data:
                new_time = user_data.remaining_week + seconds
                return interface.set_time_left_week(username, new_time)
        elif period == "month":
            user_data = get_user_data(username)
            if user_data:
                new_time = user_data.remaining_month + seconds
                return interface.set_time_left_month(username, new_time)
            
        return False
    except Exception as e:
        logger.error(f"Failed to add time to {username}: {e}")
        return False
