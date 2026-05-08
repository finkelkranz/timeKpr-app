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


def _to_python_value(value: Any) -> Any:
    """Convert dbus types to native Python types.
    
    Handles dbus.String, dbus.Int32, dbus.Array, dbus.Dictionary, etc.
    """
    if isinstance(value, dbus.String):
        return str(value)
    elif isinstance(value, (dbus.Int32, dbus.Int64, dbus.UInt32, dbus.UInt64)):
        return int(value)
    elif isinstance(value, dbus.Double):
        return float(value)
    elif isinstance(value, dbus.Boolean):
        return bool(value)
    elif isinstance(value, dbus.Array):
        return [_to_python_value(item) for item in value]
    elif isinstance(value, dbus.Dictionary):
        return {_to_python_value(k): _to_python_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [_to_python_value(item) for item in value]
    elif isinstance(value, dict):
        return {_to_python_value(k): _to_python_value(v) for k, v in value.items()}
    elif hasattr(value, "__iter__") and not isinstance(value, str):
        # Handle other iterable dbus types
        return [_to_python_value(item) for item in value]
    else:
        return value


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
        
        timekpr returns each user as [username, displayname] pair wrapped in dbus.Array.
        We extract just the usernames.
        """
        try:
            # Official API: getUserList() → (status, message, [dbus.Array([username, displayname]), ...])
            result = self.interface.getUserList()
            if isinstance(result, (list, tuple)) and len(result) >= 3:
                status, message, users_raw = result[0], result[1], result[2]
                if status == 0:  # Success
                    users = []
                    # Convert dbus types to Python types
                    users_raw = _to_python_value(users_raw)
                    
                    for user_entry in users_raw:
                        # Each entry is [username, displayname] - may still be a list or dbus.Array
                        user_entry = _to_python_value(user_entry)
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
                    # Convert dbus types to Python types
                    config = _to_python_value(config)
                    if isinstance(config, dict):
                        return config
                    return {}
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
            
            # Convert dbus types to Python types
            result = _to_python_value(result)
            
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
            # Convert dbus types to Python types
            result = _to_python_value(result)
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
            result = self.interface.setTimeLeft(username, "=", dbus.Int32(seconds))
            result = _to_python_value(result)
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
        """Set remaining time for this week.
        
        NOTE: timekpr D-Bus API setTimeLeft only supports daily (today) time.
        There is no direct D-Bus method to set weekly/monthly remaining time.
        This method sets daily time as a fallback.
        Use set_limit_week() to change the weekly limit instead.
        """
        try:
            # timekpr setTimeLeft only supports "+", "-", or "=" operations for TODAY
            result = self.interface.setTimeLeft(username, "=", dbus.Int32(seconds))
            result = _to_python_value(result)
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.warning(f"set_time_left_week: timekpr only supports daily time via setTimeLeft. Set daily time to {seconds}s for {username}")
                    return True
                else:
                    message = result[1] if len(result) > 1 else ""
                    logger.error(f"setTimeLeft failed for {username}: {message}")
            return False
        except DBusException as e:
            logger.error(f"Failed to set weekly time left for {username}: {e}")
            return False

    def set_time_left_month(self, username: str, seconds: int) -> bool:
        """Set remaining time for this month.
        
        NOTE: timekpr D-Bus API setTimeLeft only supports daily (today) time.
        There is no direct D-Bus method to set monthly remaining time.
        This method sets daily time as a fallback.
        Use set_limit_month() to change the monthly limit instead.
        """
        try:
            # timekpr setTimeLeft only supports "+", "-", or "=" operations for TODAY
            result = self.interface.setTimeLeft(username, "=", dbus.Int32(seconds))
            result = _to_python_value(result)
            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    logger.warning(f"set_time_left_month: timekpr only supports daily time via setTimeLeft. Set daily time to {seconds}s for {username}")
                    return True
                else:
                    message = result[1] if len(result) > 1 else ""
                    logger.error(f"setTimeLeft failed for {username}: {message}")
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
            # Each hour key maps to a dict with "enabled" -> 1
            hours_dict = {}
            for h in sorted(set(hours)):
                # Each hour is a string key with a nested dict
                inner_dict = {"enabled": dbus.Int32(1)}
                hours_dict[str(h)] = inner_dict
            
            result = self.interface.setAllowedHours(
                username,
                str(day),
                hours_dict,
            )
            result = _to_python_value(result)
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
            result = _to_python_value(result)
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
            result = _to_python_value(result)
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
            result = self.interface.setTimeLimitWeek(username, dbus.Int32(seconds))
            result = _to_python_value(result)
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
            result = self.interface.setTimeLimitMonth(username, dbus.Int32(seconds))
            result = _to_python_value(result)
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
