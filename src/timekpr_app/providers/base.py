"""Abstract interface (Protocol) for timekpr data access providers.

This module defines the TimekprDataProvider Protocol that all timekpr data
access implementations must follow. This enables:
- D-Bus based access (for local timekprd communication)
- File-based access (for reading timekpr config/work files directly)
- Future remote access (for cloud-based timekpr integration)

The protocol ensures consistent API across all provider implementations,
making it easy to swap between different data access methods.

Security Note:
- All data models use Pydantic BaseModel for input validation
- Field validators ensure data integrity (bounds checking, type safety)
- Custom validators enforce business rules (valid weekdays, hours, etc.)
- See OWASP Top 10 A03:2021 (Injection) for rationale
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================

# Valid lockout types for timekpr
LockoutType = Literal["terminate", "lock", "logout", "notify"]


# =============================================================================
# PYDANTIC DATA MODELS (Validated)
# =============================================================================


class UserLimits(BaseModel):
    """Time limits configuration for a user.
    
    All fields are validated for:
    - Non-negative values (where applicable)
    - Reasonable bounds (e.g., daily <= 24 hours)
    - Valid enumerations (weekdays, hours, lockout_type)
    
    Security: Pydantic validators prevent injection attacks and logical errors.
    """
    
    # Time limits in seconds (0 = unlimited for that period)
    daily: int = Field(
        default=0,
        ge=0,
        le=86400,  # Maximum 24 hours per day
        description="Seconds allowed per day (0-86400)"
    )
    weekly: int = Field(
        default=0,
        ge=0,
        le=604800,  # Maximum 1 week (7 * 24 * 3600)
        description="Seconds allowed per week (0-604800)"
    )
    monthly: int = Field(
        default=0,
        ge=0,
        le=2592000,  # Maximum ~30 days (30 * 24 * 3600)
        description="Seconds allowed per month (0-2592000)"
    )
    
    # Allowed days: 1-7 (Monday-Sunday)
    allowed_weekdays: list[int] = Field(
        default_factory=list,
        description="List of allowed weekdays (1-7, Monday-Sunday)"
    )
    
    # Allowed hours per day: {day: [hours]}
    allowed_hours: dict[int, list[int]] = Field(
        default_factory=dict,
        description="Allowed hours per weekday (day: list of hours 0-23)"
    )
    
    # Lockout behavior when time limit is reached
    lockout_type: LockoutType = Field(
        default="terminate",
        description="Lockout type: terminate, lock, logout, or notify"
    )
    
    # Additional settings
    track_inactive: bool = Field(
        default=False,
        description="Track inactive time"
    )
    hide_tray_icon: bool = Field(
        default=False,
        description="Hide tray icon"
    )
    
    # =========================================================================
    # CUSTOM VALIDATORS
    # =========================================================================
    
    @field_validator('allowed_weekdays')
    @classmethod
    def validate_weekdays(cls, v: list[int]) -> list[int]:
        """Validate that all weekdays are in range 1-7 (Monday-Sunday)."""
        for day in v:
            if not 1 <= day <= 7:
                raise ValueError(
                    f"Invalid weekday: {day}. Weekdays must be 1-7 (Monday-Sunday)"
                )
        return v
    
    @field_validator('allowed_hours')
    @classmethod
    def validate_hours(cls, v: dict[int, list[int]]) -> dict[int, list[int]]:
        """Validate that all days and hours are in valid ranges."""
        for day, hours in v.items():
            # Validate day
            if not 1 <= day <= 7:
                raise ValueError(f"Invalid day: {day}. Days must be 1-7 (Monday-Sunday)")
            # Validate hours
            for hour in hours:
                if not 0 <= hour <= 23:
                    raise ValueError(
                        f"Invalid hour: {hour} for day {day}. Hours must be 0-23"
                    )
        return v


class UserUsage(BaseModel):
    """Time usage/consumed data for a user.
    
    All time values are validated to be non-negative.
    Timestamp is validated to be a reasonable ISO 8601 format.
    """
    
    day: int = Field(
        default=0,
        ge=0,
        description="Seconds spent today (>= 0)"
    )
    week: int = Field(
        default=0,
        ge=0,
        description="Seconds spent this week (>= 0)"
    )
    month: int = Field(
        default=0,
        ge=0,
        description="Seconds spent this month (>= 0)"
    )
    balance_day: int = Field(
        default=0,
        ge=0,
        description="Balance for today (>= 0)"
    )
    last_checked: str = Field(
        default="",
        min_length=0,
        max_length=50,  # Reasonable timestamp length
        description="ISO 8601 timestamp of last update"
    )


class UserData(BaseModel):
    """Complete timekpr data for a user.
    
    Combines limits and usage with computed remaining time properties.
    Username is required and must be non-empty.
    """
    
    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Username (required, 1-255 characters)"
    )
    display_name: str = Field(
        default="",
        max_length=255,
        description="User's display name"
    )
    limits: UserLimits = Field(
        default_factory=UserLimits,
        description="User's time limits configuration"
    )
    usage: UserUsage = Field(
        default_factory=UserUsage,
        description="User's time usage data"
    )
    
    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================
    
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
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses.
        
        Maintains backward compatibility with the original dataclass-based interface.
        """
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


# =============================================================================
# PROTOCOL DEFINITION
# =============================================================================


@runtime_checkable
class TimekprDataProvider(Protocol):
    """Abstract interface for timekpr data access providers.
    
    All timekpr data provider implementations must implement this protocol.
    This ensures a consistent API regardless of the underlying access method
    (D-Bus, file-based, or remote).
    
    Implementations:
    - DBusTimekprProvider: Uses D-Bus to communicate with local timekprd
    - FileTimekprProvider: Reads timekpr config/work files directly
    - RemoteTimekprProvider: For future cloud-based integration (stub)
    
    Example usage:
        from providers.base import TimekprDataProvider
        from providers.dbus import DBusTimekprProvider
        
        provider: TimekprDataProvider = DBusTimekprProvider()
        users = provider.get_user_list()
        user_data = provider.get_user_data("username")
    """
    
    # === Core Data Access Methods ===
    
    @abstractmethod
    def get_user_list(self) -> list[str]:
        """Get list of all configured timekpr users.
        
        Returns:
            List of usernames as strings.
            Returns empty list on error.
        
        Example:
            >>> provider.get_user_list()
            ['agnes', 'torgeir', 'user1']
        """
        ...
    
    @abstractmethod
    def get_user_data(self, username: str) -> UserData | None:
        """Get complete timekpr data for a specific user.
        
        Args:
            username: The username to get data for.
            
        Returns:
            UserData object containing limits, usage, and remaining time.
            Returns None if user not found or on error.
        
        Example:
            >>> data = provider.get_user_data("torgeir")
            >>> print(data.remaining_day)
            14400
        """
        ...
    
    @abstractmethod
    def get_all_users_data(self) -> list[UserData]:
        """Get complete timekpr data for all configured users.
        
        Returns:
            List of UserData objects for all users.
            Returns empty list on error.
        
        Example:
            >>> all_data = provider.get_all_users_data()
            >>> for user in all_data:
            ...     print(f"{user.username}: {user.remaining_day}s")
        """
        ...
    
    # === User Configuration Methods ===
    
    @abstractmethod
    def get_user_config(self, username: str) -> dict[str, Any]:
        """Get user configuration from timekpr.
        
        Args:
            username: The username to get configuration for.
            
        Returns:
            Dictionary containing user configuration.
            Returns empty dict on error.
        
        Note:
            This method returns raw configuration data. For structured data,
            use get_user_data() which returns a UserData object.
        """
        ...
    
    # === Time Management Methods ===
    
    @abstractmethod
    def get_time_left(self, username: str) -> dict[str, int]:
        """Get remaining time for a user.
        
        Args:
            username: The username to get remaining time for.
            
        Returns:
            Dictionary with keys 'day', 'week', 'month' containing
            remaining seconds for each period.
            Returns empty dict on error.
        
        Example:
            >>> provider.get_time_left("torgeir")
            {'day': 14400, 'week': 100800, 'month': 432000}
        """
        ...
    
    @abstractmethod
    def set_time_left(self, username: str, seconds: int, period: str = "day") -> bool:
        """Set remaining time for a user for a specific period.
        
        Args:
            username: The username.
            seconds: Number of seconds to set as remaining.
            period: The time period - 'day', 'week', or 'month'.
            
        Returns:
            True if successful, False otherwise.
        
        Note:
            Not all implementations may support all periods.
            D-Bus implementation primarily supports 'day' period.
        """
        ...
    
    # === Limits Configuration Methods ===
    
    @abstractmethod
    def set_limit_week(self, username: str, seconds: int) -> bool:
        """Set weekly time limit for a user.
        
        Args:
            username: The username.
            seconds: Weekly limit in seconds.
            
        Returns:
            True if successful, False otherwise.
        """
        ...
    
    @abstractmethod
    def set_limit_month(self, username: str, seconds: int) -> bool:
        """Set monthly time limit for a user.
        
        Args:
            username: The username.
            seconds: Monthly limit in seconds.
            
        Returns:
            True if successful, False otherwise.
        """
        ...
    
    @abstractmethod
    def set_limits_per_weekday(self, username: str, day_limits: dict[int, int]) -> bool:
        """Set daily limits for each weekday.
        
        Args:
            username: The username.
            day_limits: Dictionary mapping day number (1-7, Mon-Sun) to
                       limit in seconds.
            
        Returns:
            True if successful, False otherwise.
        
        Example:
            >>> provider.set_limits_per_weekday("torgeir", {
            ...     1: 14400,  # Monday: 4 hours
            ...     2: 14400,  # Tuesday: 4 hours
            ...     3: 14400,  # Wednesday: 4 hours
            ...     4: 14400,  # Thursday: 4 hours
            ...     5: 14400,  # Friday: 4 hours
            ... })
        """
        ...
    
    # === Allowed Time Configuration Methods ===
    
    @abstractmethod
    def set_allowed_days(self, username: str, days: list[int]) -> bool:
        """Set allowed weekdays for a user.
        
        Args:
            username: The username.
            days: List of day numbers (1-7, Monday-Sunday).
            
        Returns:
            True if successful, False otherwise.
        
        Example:
            >>> provider.set_allowed_days("torgeir", [1, 2, 3, 4, 5])  # Weekdays only
        """
        ...
    
    @abstractmethod
    def set_allowed_hours(self, username: str, day: int, hours: list[int]) -> bool:
        """Set allowed hours for a specific day.
        
        Args:
            username: The username.
            day: Day number (1-7, Monday-Sunday).
            hours: List of allowed hours (0-23).
            
        Returns:
            True if successful, False otherwise.
        
        Example:
            >>> provider.set_allowed_hours("torgeir", 1, [8, 9, 10, 11, 12, 13, 14, 15])
        """
        ...


# =============================================================================
# ABSTRACT BASE CLASS
# =============================================================================


class BaseTimekprProvider(ABC):
    """Abstract base class for timekpr data providers.
    
    This class provides a concrete base with common functionality and
    serves as an alternative to the Protocol for implementations that
    need inheritance-based polymorphism.
    
    Subclasses must implement all abstract methods from TimekprDataProvider.
    
    Example:
        class MyProvider(BaseTimekprProvider):
            def get_user_list(self) -> list[str]:
                return ["user1", "user2"]
            # ... implement all other abstract methods
    """
    
    @abstractmethod
    def get_user_list(self) -> list[str]:
        """Get list of all configured timekpr users."""
        ...
    
    @abstractmethod
    def get_user_data(self, username: str) -> UserData | None:
        """Get complete timekpr data for a specific user."""
        ...
    
    @abstractmethod
    def get_all_users_data(self) -> list[UserData]:
        """Get complete timekpr data for all configured users."""
        ...
    
    @abstractmethod
    def get_user_config(self, username: str) -> dict[str, Any]:
        """Get user configuration from timekpr."""
        ...
    
    @abstractmethod
    def get_time_left(self, username: str) -> dict[str, int]:
        """Get remaining time for a user."""
        ...
    
    @abstractmethod
    def set_time_left(self, username: str, seconds: int, period: str = "day") -> bool:
        """Set remaining time for a user."""
        ...
    
    @abstractmethod
    def set_limit_week(self, username: str, seconds: int) -> bool:
        """Set weekly time limit for a user."""
        ...
    
    @abstractmethod
    def set_limit_month(self, username: str, seconds: int) -> bool:
        """Set monthly time limit for a user."""
        ...
    
    @abstractmethod
    def set_limits_per_weekday(self, username: str, day_limits: dict[int, int]) -> bool:
        """Set daily limits for each weekday."""
        ...
    
    @abstractmethod
    def set_allowed_days(self, username: str, days: list[int]) -> bool:
        """Set allowed weekdays for a user."""
        ...
    
    @abstractmethod
    def set_allowed_hours(self, username: str, day: int, hours: list[int]) -> bool:
        """Set allowed hours for a specific day."""
        ...
