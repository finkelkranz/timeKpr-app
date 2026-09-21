"""Timekpr data providers package.

This package provides multiple implementations for accessing timekpr data:
- DBusTimekprProvider: D-Bus based access to local timekprd
- FileTimekprProvider: File-based access to timekpr config/work files
- RemoteTimekprProvider: Stub for future remote/cloud integration

The package exposes a common TimekprDataProvider Protocol that all
implementations follow, enabling easy switching between providers.

Example usage:
    from timekpr_app.providers.base import TimekprDataProvider, UserData
    from timekpr_app.providers.dbus import DBusTimekprProvider
    
    provider: TimekprDataProvider = DBusTimekprProvider()
    users = provider.get_user_list()
    user_data: UserData = provider.get_user_data("username")

For dependency injection, use the provider factory:
    from timekpr_app.providers import get_provider
    
    provider = get_provider()  # Returns appropriate provider based on config
"""

from timekpr_app.providers.base import (
    BaseTimekprProvider,
    TimekprDataProvider,
    UserData,
    UserLimits,
    UserUsage,
)

# Re-export for convenience
__all__ = [
    "BaseTimekprProvider",
    "TimekprDataProvider",
    "UserData",
    "UserLimits",
    "UserUsage",
    "get_provider",
    "create_provider",
]


def create_provider(provider_type: str = None) -> TimekprDataProvider:
    """Create a timekpr provider instance.
    
    Args:
        provider_type: Type of provider - 'dbus', 'file', or 'remote'.
                      If None, uses environment configuration or defaults.
    
    Returns:
        A TimekprDataProvider instance.
    
    Raises:
        ValueError: If provider_type is not recognized.
        ImportError: If the requested provider module cannot be imported.
    """
    if provider_type is None:
        # Try to determine from environment or use default
        import os
        provider_type = os.environ.get("TIMEKPR_PROVIDER", "dbus")
    
    if provider_type == "dbus":
        from timekpr_app.providers.dbus import DBusTimekprProvider
        return DBusTimekprProvider()
    elif provider_type == "file":
        from timekpr_app.providers.file import FileTimekprProvider
        return FileTimekprProvider()
    elif provider_type == "remote":
        from timekpr_app.providers.remote import RemoteTimekprProvider
        return RemoteTimekprProvider()
    else:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Valid types: 'dbus', 'file', 'remote'"
        )


def get_provider() -> TimekprDataProvider:
    """Get the configured timekpr provider instance.
    
    This function returns a singleton provider instance based on
    the configured provider type (from environment variable TIMEKPR_PROVIDER).
    
    Default: DBusTimekprProvider (for local timekprd communication)
    
    Returns:
        A TimekprDataProvider instance.
    
    Example:
        provider = get_provider()
        users = provider.get_user_list()
    """
    import os
    
    # Check environment for provider type
    provider_type = os.environ.get("TIMEKPR_PROVIDER", "dbus")
    
    # For now, return a new instance each time
    # In the future, this could be a singleton
    return create_provider(provider_type)
