"""Tests for timekpr D-Bus interface using mock data."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from timekpr_app.timekpr import (
    TimekprDBusInterface,
    _to_python_value,
    get_timekpr_interface,
)
from timekpr_app.timekpr_mock import MockTimekprDBusInterface


class TestToPythonValue:
    """Tests for _to_python_value helper function."""

    def test_string_conversion(self) -> None:
        """Test dbus.String to str conversion."""
        import dbus
        
        value = dbus.String("test")
        assert _to_python_value(value) == "test"

    def test_int32_conversion(self) -> None:
        """Test dbus.Int32 to int conversion."""
        import dbus
        
        value = dbus.Int32(42)
        assert _to_python_value(value) == 42

    def test_int64_conversion(self) -> None:
        """Test dbus.Int64 to int conversion."""
        import dbus
        
        value = dbus.Int64(42)
        assert _to_python_value(value) == 42

    def test_array_conversion(self) -> None:
        """Test dbus.Array to list conversion."""
        import dbus
        
        value = dbus.Array([dbus.String("a"), dbus.String("b")], signature="s")
        assert _to_python_value(value) == ["a", "b"]

    def test_nested_array_conversion(self) -> None:
        """Test nested dbus.Array conversion."""
        import dbus
        
        # This simulates the structure returned by getUserList()
        inner1 = dbus.Array([dbus.String("agnes"), dbus.String("")], signature="s")
        inner2 = dbus.Array([dbus.String("torgeir"), dbus.String("Torgeir")], signature="s")
        value = dbus.Array([inner1, inner2], signature="as")
        result = _to_python_value(value)
        
        assert len(result) == 2
        assert result[0] == ["agnes", ""]
        assert result[1] == ["torgeir", "Torgeir"]

    def test_dict_conversion(self) -> None:
        """Test dbus.Dictionary conversion."""
        import dbus
        
        # Create a simple dbus dict
        value = {"key1": dbus.String("value1"), "key2": dbus.Int32(42)}
        result = _to_python_value(value)
        
        assert result == {"key1": "value1", "key2": 42}

    def test_list_conversion(self) -> None:
        """Test regular list conversion (passthrough)."""
        value = [1, 2, 3]
        assert _to_python_value(value) == [1, 2, 3]

    def test_tuple_conversion(self) -> None:
        """Test tuple conversion."""
        value = (1, 2, 3)
        assert _to_python_value(value) == [1, 2, 3]

    def test_bool_conversion(self) -> None:
        """Test dbus.Boolean to bool conversion."""
        import dbus
        
        assert _to_python_value(dbus.Boolean(True)) is True
        assert _to_python_value(dbus.Boolean(False)) is False

    def test_none_passthrough(self) -> None:
        """Test that None passes through unchanged."""
        assert _to_python_value(None) is None

    def test_plain_types_passthrough(self) -> None:
        """Test that plain Python types pass through unchanged."""
        assert _to_python_value("string") == "string"
        assert _to_python_value(42) == 42
        assert _to_python_value(3.14) == 3.14
        assert _to_python_value(True) is True


class TestMockTimekprDBusInterface:
    """Tests using the mock interface for safe testing."""

    @pytest.fixture
    def mock_interface(self) -> MockTimekprDBusInterface:
        """Create a fresh mock interface for each test."""
        from timekpr_app.timekpr_mock import reset_mock_users
        reset_mock_users()
        return MockTimekprDBusInterface()

    def test_get_user_list(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test getting user list from mock."""
        users = mock_interface.get_user_list()
        
        assert isinstance(users, list)
        assert "testuser" in users

    def test_get_user_config(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test getting user config from mock."""
        config = mock_interface.get_user_config("testuser")
        
        assert isinstance(config, dict)
        assert config is not None
        assert len(config) > 0

    def test_get_user_config_nonexistent(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test getting config for non-existent user."""
        config = mock_interface.get_user_config("nonexistent")
        
        assert config == {}

    def test_get_time_left(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test getting time left from mock."""
        time_left = mock_interface.get_time_left("testuser")
        
        assert isinstance(time_left, dict)
        assert "day" in time_left
        assert "week" in time_left
        assert "month" in time_left
        assert time_left["day"] > 0

    def test_get_time_left_nonexistent(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test getting time left for non-existent user."""
        time_left = mock_interface.get_time_left("nonexistent")
        
        assert time_left == {"day": 0, "week": 0, "month": 0}

    def test_set_time_left_day(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting time left for today."""
        result = mock_interface.set_time_left_day("testuser", 7200)
        
        assert result is True

    def test_set_time_left_day_nonexistent(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting time for non-existent user fails."""
        result = mock_interface.set_time_left_day("nonexistent", 7200)
        
        assert result is False

    def test_set_time_left_week(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting weekly time left."""
        result = mock_interface.set_time_left_week("testuser", 50400)
        
        assert result is True

    def test_set_time_left_month(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting monthly time left."""
        result = mock_interface.set_time_left_month("testuser", 302400)
        
        assert result is True

    def test_set_allowed_hours(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting allowed hours for a day."""
        hours = [8, 9, 10, 11, 12, 13, 14, 15]
        result = mock_interface.set_allowed_hours("testuser", 1, hours)
        
        assert result is True

    def test_set_allowed_hours_invalid_day(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting allowed hours with invalid day."""
        result = mock_interface.set_allowed_hours("testuser", 0, [8, 9])
        
        assert result is False

    def test_set_allowed_hours_nonexistent(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting allowed hours for non-existent user."""
        result = mock_interface.set_allowed_hours("nonexistent", 1, [8, 9])
        
        assert result is False

    def test_set_allowed_days(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting allowed days."""
        days = [1, 2, 3, 4, 5]  # Mon-Fri
        result = mock_interface.set_allowed_days("testuser", days)
        
        assert result is True

    def test_set_allowed_days_invalid(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting allowed days with invalid day."""
        result = mock_interface.set_allowed_days("testuser", [0, 8])
        
        assert result is False

    def test_set_allowed_days_nonexistent(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting allowed days for non-existent user."""
        result = mock_interface.set_allowed_days("nonexistent", [1, 2, 3])
        
        assert result is False

    def test_set_limits_per_weekday(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting daily limits per weekday."""
        day_limits = {
            1: 14400,  # Monday: 4 hours
            2: 14400,  # Tuesday: 4 hours
            3: 14400,  # Wednesday: 4 hours
            4: 14400,  # Thursday: 4 hours
            5: 14400,  # Friday: 4 hours
            6: 21600,  # Saturday: 6 hours
            7: 21600,  # Sunday: 6 hours
        }
        result = mock_interface.set_limits_per_weekday("testuser", day_limits)
        
        assert result is True

    def test_set_limit_week(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting weekly limit."""
        result = mock_interface.set_limit_week("testuser", 100800)
        
        assert result is True

    def test_set_limit_month(self, mock_interface: MockTimekprDBusInterface) -> None:
        """Test setting monthly limit."""
        result = mock_interface.set_limit_month("testuser", 504000)
        
        assert result is True


class TestTimekprDBusInterfaceWithMock:
    """Tests for TimekprDBusInterface using mocked D-Bus to avoid real calls."""

    @pytest.fixture
    def patched_interface(self) -> TimekprDBusInterface:
        """Create interface with mocked D-Bus."""
        with patch("timekpr_app.timekpr.dbus.SystemBus") as mock_bus:
            # Setup mock D-Bus
            mock_bus_instance = MagicMock()
            mock_bus.return_value = mock_bus_instance
            
            mock_proxy = MagicMock()
            mock_bus_instance.get_object.return_value = mock_proxy
            
            mock_admin_iface = MagicMock()
            mock_limits_iface = MagicMock()
            mock_bus_instance.get_object.return_value.get_object = MagicMock()
            
            # Make Interface() return our mock interfaces
            def get_interface(interface_name: str) -> MagicMock:
                if "admin" in interface_name:
                    return mock_admin_iface
                elif "limits" in interface_name:
                    return mock_limits_iface
                return MagicMock()
            
            mock_proxy.get_object = MagicMock(side_effect=get_interface)
            
            return TimekprDBusInterface()

    def test_helper_function_exists(self) -> None:
        """Test that _to_python_value helper exists and is callable."""
        assert callable(_to_python_value)


class TestGetTimekprInterface:
    """Tests for the global interface getter."""

    def test_singleton_behavior(self) -> None:
        """Test that get_timekpr_interface returns a singleton."""
        # Reset global state
        import timekpr_app.timekpr as timekpr_module
        timekpr_module._timekpr_interface = None
        
        with patch("timekpr_app.timekpr.TimekprDBusInterface") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance
            
            iface1 = get_timekpr_interface()
            iface2 = get_timekpr_interface()
            
            assert iface1 is iface2
            mock_class.assert_called_once()
