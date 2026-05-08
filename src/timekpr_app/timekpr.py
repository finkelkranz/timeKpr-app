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
        """Get list of configured users.
        
        timekpr returns each user as [username, displayname] pair.
        We extract just the usernames.
        """
        try:
            # Official API: getUserList() → (status, message, [[username, displayname], ...])
            result = self.interface.getUserList()
            if isinstance(result, (list, tuple)) and len(result) >= 3:
                status, message, users_raw = result[0], result[1], result[2]
                if status == 0:  # Success
                    users = []
                    for user_entry in users_raw:
                        # Each entry is [username, displayname]
                        if isinstance(user_entry, (list, tuple)) and len(user_entry) >= 1:
                            username = str(user_entry[0])
                            users.append(username)
                    logger.info(f"Found {len(users)} users: {users}")
                    return users
                else:
                    logger.error(f"timekpr getUserList failed: {message}")
                    return []
            return []
        except DBusException as e:
            logger.error(f"Failed to get user list: {e}")
            return []

    def get_user_config(self, username: str) -> dict[str, Any]:
        """Get user configuration from timekpr."""
        try:
            # Official API: getUserInformation(username, infolevel) → (status, message, config_dict)
            result = self.interface.getUserInformation(username, "")
            if isinstance(result, (list, tuple)) and len(result) >= 3:
                status, message, config = result[0], result[1], result[2]
                if status == 0:  # Success
                    return dict(config) if config else {}
                else:
                    logger.error(f"timekpr getUserInformation failed for {username}: {message}")
                    return {}
            return {}
        except DBusException as e:
            logger.error(f"Failed to get config for user {username}: {e}")
            return {}

    def get_time_left(self, username: str) -> dict[str, int]:
        """Get remaining time for user (today, week, month).
        
        Note: Official timekpr returns time via D-Bus signals after requestTimeLeft().
        This is a simplified implementation that returns mock data for UI testing.
        TODO: Implement proper D-Bus signal listening for real-time updates.
        """
        try:
            # Try to request time from limits interface
            limits_interface = dbus.Interface(self.proxy, TIMEKPR_DBUS_LIMITS_INTERFACE)
            result = limits_interface.requestTimeLeft(username)
            
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                message = result[1] if len(result) > 1 else ""
                
                if status == 0:  # Success - time would come via signals
                    logger.info(f"requestTimeLeft for {username} returned signal-based times")
                    # For now, return mock data so UI works
                    # TODO: Implement signal listener
                    return {
                        "day": 14400,      # 4 hours
                        "week": 100800,    # 28 hours
                        "month": 432000,   # 120 hours
                    }
                else:
                    logger.warning(f"requestTimeLeft failed for {username}: {message}")
                    return {
                        "day": 0,
                        "week": 0,
                        "month": 0,
                    }
            return {}
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
            # Official API: setTimeLeft(username, operation, seconds) → (status, message)
            # operation: "+", "-", or "="
            result = self.interface.setTimeLeft(username, "=", int(seconds))
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set daily time left for {username} to {seconds}s")
                    return True
                else:
                    logger.error(f"setTimeLeft failed: {result}")
                    return False
            return True
        except DBusException as e:
            logger.error(f"Failed to set time left for {username}: {e}")
            return False

    def set_time_left_week(self, username: str, seconds: int) -> bool:
        """Set remaining time for this week."""
        try:
            result = self.interface.setTimeLeft(username, "week", int(seconds))
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set weekly time left for {username} to {seconds}s")
                    return True
            return False
        except DBusException as e:
            logger.error(f"Failed to set weekly time left for {username}: {e}")
            return False

    def set_time_left_month(self, username: str, seconds: int) -> bool:
        """Set remaining time for this month."""
        try:
            result = self.interface.setTimeLeft(username, "month", int(seconds))
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set monthly time left for {username} to {seconds}s")
                    return True
            return False
        except DBusException as e:
            logger.error(f"Failed to set monthly time left for {username}: {e}")
            return False

    def set_allowed_hours(self, username: str, day: int, hours: list[int]) -> bool:
        """Set allowed hours for specific day (1=Monday, 7=Sunday).
        
        D-Bus signature: setAllowedHours(s, s, a{sa{si}}, ...)
        hours_dict should be: {"8": {"enabled": 1}, "9": {"enabled": 1}, ...}
        """
        try:
            # Convert hours list to D-Bus dict format: {"8": {"enabled": 1}, ...}
            hours_dict = {
                str(h): {"enabled": dbus.Int32(1)}
                for h in sorted(set(hours))
            }
            result = self.interface.setAllowedHours(
                username,
                str(day),
                hours_dict,
            )
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set allowed hours for {username} on day {day}: {hours}")
                    return True
                else:
                    message = result[1] if len(result) > 1 else ""
                    logger.error(f"setAllowedHours failed: {message}")
            return False
        except DBusException as e:
            logger.error(f"Failed to set allowed hours for {username}: {e}")
            return False

    def set_allowed_days(self, username: str, days: list[int]) -> bool:
        """Set allowed weekdays (1=Monday, 7=Sunday).
        
        D-Bus signature: setAllowedDays(s, as, ...)
        days should be: ["1", "2", "3", "4", "5"] (array of strings)
        """
        try:
            # Convert to array of strings as D-Bus expects
            days_array = [str(d) for d in sorted(set(days))]
            result = self.interface.setAllowedDays(username, days_array)
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set allowed days for {username}: {days}")
                    return True
                else:
                    message = result[1] if len(result) > 1 else ""
                    logger.error(f"setAllowedDays failed: {message}")
            return False
        except DBusException as e:
            logger.error(f"Failed to set allowed days for {username}: {e}")
            return False

    def set_limits_per_weekday(self, username: str, day_limits: dict[int, int]) -> bool:
        """Set daily limits for each weekday in seconds.
        
        D-Bus signature: setTimeLimitForDays(s, ai, ...)
        day_limits should be: [14400, 14400, ...] (array of ints, Mon-Sun)
        """
        try:
            # Convert dict to array of ints as D-Bus expects
            # Order: Monday (1) through Sunday (7)
            limits_array = [
                dbus.Int32(day_limits.get(d, 86400))
                for d in range(1, 8)
            ]
            result = self.interface.setTimeLimitForDays(username, limits_array)
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set daily limits for {username}: {day_limits}")
                    return True
                else:
                    message = result[1] if len(result) > 1 else ""
                    logger.error(f"setTimeLimitForDays failed: {message}")
            return False
        except DBusException as e:
            logger.error(f"Failed to set daily limits for {username}: {e}")
            return False

    def set_limit_week(self, username: str, seconds: int) -> bool:
        """Set weekly limit in seconds."""
        try:
            result = self.interface.setTimeLimitWeek(username, int(seconds))
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set weekly limit for {username} to {seconds}s")
                    return True
            return False
        except DBusException as e:
            logger.error(f"Failed to set weekly limit for {username}: {e}")
            return False

    def set_limit_month(self, username: str, seconds: int) -> bool:
        """Set monthly limit in seconds."""
        try:
            result = self.interface.setTimeLimitMonth(username, int(seconds))
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.info(f"Set monthly limit for {username} to {seconds}s")
                    return True
            return False
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
