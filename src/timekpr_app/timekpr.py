"""D-Bus interface to timekprd daemon."""

from __future__ import annotations

import logging
from typing import Any

import dbus
from dbus import DBusException

logger = logging.getLogger(__name__)

# D-Bus constants (from timekpr source)
TIMEKPR_DBUS_BUS_NAME = "com.timekpr.server"
TIMEKPR_DBUS_SERVER_PATH = "/com/timekpr/server"
TIMEKPR_DBUS_ADMIN_INTERFACE = "com.timekpr.server.user.admin"
TIMEKPR_DBUS_LIMITS_INTERFACE = "com.timekpr.server.user.limits"


class TimekprDBusInterface:
    """Wrapper for timekprd D-Bus interface."""

    def __init__(self) -> None:
        """Initialize D-Bus connection to timekprd."""
        try:
            # Use SystemBus to talk to timekprd (running as root)
            self.bus = dbus.SystemBus()
            self.proxy = self.bus.get_object(
                TIMEKPR_DBUS_BUS_NAME,
                TIMEKPR_DBUS_SERVER_PATH,
            )
            self.interface = dbus.Interface(
                self.proxy,
                TIMEKPR_DBUS_ADMIN_INTERFACE,
            )
            logger.info("Connected to timekprd via D-Bus")
        except DBusException as e:
            logger.error(f"Failed to connect to timekprd: {e}")
            raise

    def get_user_list(self) -> list[str]:
        """Get list of configured users."""
        try:
            result = self.interface.RequestUserList()
            # Result is dbus.Array of strings
            return list(result)
        except DBusException as e:
            logger.error(f"Failed to get user list: {e}")
            return []

    def get_user_config(self, username: str) -> dict[str, Any]:
        """Get user configuration from timekpr."""
        try:
            # getUserInformation returns (status, message, config_dict)
            result = self.interface.getUserInformation(username, "")
            if len(result) >= 3:
                return dict(result[2])  # Third element is config dict
            return {}
        except DBusException as e:
            logger.error(f"Failed to get config for user {username}: {e}")
            return {}

    def get_time_left(self, username: str) -> dict[str, int]:
        """Get remaining time for user (today, week, month)."""
        try:
            result = self.interface.RequestTimeLeft(username)
            return dict(result)
        except DBusException as e:
            logger.error(f"Failed to get time left for user {username}: {e}")
            return {}

    def get_time_limits(self, username: str) -> dict[str, Any]:
        """Get user's time limits."""
        try:
            # Use the limits interface for time limits
            limits_interface = dbus.Interface(self.proxy, TIMEKPR_DBUS_LIMITS_INTERFACE)
            result = limits_interface.requestTimeLimits(username)
            # Result is (status, message) - limits come via signals
            # For now, return empty dict since we need to handle signals
            return {}
        except DBusException as e:
            logger.error(f"Failed to get time limits for user {username}: {e}")
            return {}

    def set_time_left_day(self, username: str, seconds: int) -> bool:
        """Set remaining time for today (admin operation)."""
        try:
            # SetTimeLeft takes: username, operation ("day"/"week"/"month"), seconds
            self.interface.SetTimeLeft(username, "day", int(seconds))
            logger.info(f"Set daily time left for {username} to {seconds}s")
            return True
        except DBusException as e:
            logger.error(f"Failed to set time left for {username}: {e}")
            return False

    def set_time_left_week(self, username: str, seconds: int) -> bool:
        """Set remaining time for this week."""
        try:
            self.interface.SetTimeLeft(username, "week", int(seconds))
            logger.info(f"Set weekly time left for {username} to {seconds}s")
            return True
        except DBusException as e:
            logger.error(f"Failed to set weekly time left for {username}: {e}")
            return False

    def set_time_left_month(self, username: str, seconds: int) -> bool:
        """Set remaining time for this month."""
        try:
            self.interface.SetTimeLeft(username, "month", int(seconds))
            logger.info(f"Set monthly time left for {username} to {seconds}s")
            return True
        except DBusException as e:
            logger.error(f"Failed to set monthly time left for {username}: {e}")
            return False

    def set_allowed_hours(self, username: str, day: int, hours: list[int]) -> bool:
        """Set allowed hours for specific day (1=Monday, 7=Sunday)."""
        try:
            # Convert to semicolon-separated string as timekpr expects
            hours_str = ";".join(str(h) for h in sorted(set(hours)))
            self.interface.SetAllowedHours(username, day, hours_str)
            logger.info(f"Set allowed hours for {username} on day {day}: {hours_str}")
            return True
        except DBusException as e:
            logger.error(f"Failed to set allowed hours for {username}: {e}")
            return False

    def set_allowed_days(self, username: str, days: list[int]) -> bool:
        """Set allowed weekdays (1=Monday, 7=Sunday)."""
        try:
            # Convert to semicolon-separated string
            days_str = ";".join(str(d) for d in sorted(set(days)))
            self.interface.SetAllowedDays(username, days_str)
            logger.info(f"Set allowed days for {username}: {days_str}")
            return True
        except DBusException as e:
            logger.error(f"Failed to set allowed days for {username}: {e}")
            return False

    def set_limits_per_weekday(self, username: str, day_limits: dict[int, int]) -> bool:
        """Set daily limits for each weekday in seconds."""
        try:
            # Convert dict to semicolon-separated string
            # day_limits: {1: 14400, 2: 14400, ...} (where 1 = Monday, etc.)
            limits_str = ";".join(
                str(day_limits.get(d, 86400)) for d in range(1, 8)
            )
            self.interface.SetLimitsPerWeekday(username, limits_str)
            logger.info(f"Set daily limits for {username}: {limits_str}")
            return True
        except DBusException as e:
            logger.error(f"Failed to set daily limits for {username}: {e}")
            return False

    def set_limit_week(self, username: str, seconds: int) -> bool:
        """Set weekly limit in seconds."""
        try:
            self.interface.SetLimitWeek(username, int(seconds))
            logger.info(f"Set weekly limit for {username} to {seconds}s")
            return True
        except DBusException as e:
            logger.error(f"Failed to set weekly limit for {username}: {e}")
            return False

    def set_limit_month(self, username: str, seconds: int) -> bool:
        """Set monthly limit in seconds."""
        try:
            self.interface.SetLimitMonth(username, int(seconds))
            logger.info(f"Set monthly limit for {username} to {seconds}s")
            return True
        except DBusException as e:
            logger.error(f"Failed to set monthly limit for {username}: {e}")
            return False


# Global instance
_timekpr_interface: TimekprDBusInterface | None = None


def get_timekpr_interface() -> TimekprDBusInterface:
    """Get or create timekpr D-Bus interface."""
    global _timekpr_interface
    if _timekpr_interface is None:
        _timekpr_interface = TimekprDBusInterface()
    return _timekpr_interface
