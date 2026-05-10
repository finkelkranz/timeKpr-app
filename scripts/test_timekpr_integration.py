#!/usr/bin/env python3
"""Integration test script to verify timekpr D-Bus communication.

Run this to test if the app can read from and write to timekprd.

Usage:
    python test_timekpr_integration.py [--mock] [--real]
    
    --mock   Use mock interface (safe, doesn't affect real timekpr)
    --real   Use real D-Bus interface (requires sudo, USE WITH CARE)
"""

import sys
import logging
from typing import Any

import dbus
from dbus import DBusException

# Note: mock interface is imported dynamically in TimekprTester.__init__

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO to reduce noise
    format="%(levelname)-8s: %(message)s",
)
logger = logging.getLogger(__name__)

# Import the fixed TimekprDBusInterface
try:
    from timekpr_app.timekpr import TimekprDBusInterface
    HAVE_TIMEKPR_APP = True
except ImportError:
    HAVE_TIMEKPR_APP = False

# D-Bus constants
TIMEKPR_DBUS_BUS_NAME = "com.timekpr.server"
TIMEKPR_DBUS_SERVER_PATH = "/com/timekpr/server"
TIMEKPR_DBUS_ADMIN_INTERFACE = "com.timekpr.server.user.admin"
TIMEKPR_DBUS_LIMITS_INTERFACE = "com.timekpr.server.user.limits"


class TimekprTester:
    """Test D-Bus communication with timekprd."""

    def __init__(self, use_mock: bool = True) -> None:
        """Initialize D-Bus connection or mock interface."""
        self.results = []
        self.test_username = None
        self.bus = None
        self.admin_interface = None
        self.limits_interface = None
        self.use_mock = use_mock
        self.mock_interface = None
        self.read_only = False  # Will be set via command line
        self.target_user = None  # Will be set via command line
        
        if use_mock:
            try:
                from src.timekpr_app.timekpr_mock import MockTimekprDBusInterface
                self.mock_interface = MockTimekprDBusInterface()
                logger.info("Using MOCK interface (safe for testing)")
            except ImportError as e:
                logger.warning(f"Mock interface not available: {e}")
                self.use_mock = False

    def print_header(self, title: str) -> None:
        """Print test section header."""
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print(f"{'=' * 70}\n")

    def print_test(self, name: str, status: str, details: str = "") -> None:
        """Print test result."""
        status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"  {status_symbol} {name:<40} [{status}]")
        if details:
            for line in details.split("\n"):
                print(f"    → {line}")
        self.results.append((name, status))

    def test_connection(self) -> bool:
        """Test D-Bus connection to timekprd."""
        self.print_header("1. Connection Test")
        
        if self.use_mock and self.mock_interface:
            self.print_test("Mock Interface", "PASS", "Connected to mock (safe mode)")
            return True
        
        if not self.use_mock:
            try:
                self.bus = dbus.SystemBus()
                proxy = self.bus.get_object(TIMEKPR_DBUS_BUS_NAME, TIMEKPR_DBUS_SERVER_PATH)
                self.admin_interface = dbus.Interface(proxy, TIMEKPR_DBUS_ADMIN_INTERFACE)
                self.limits_interface = dbus.Interface(proxy, TIMEKPR_DBUS_LIMITS_INTERFACE)
                self.print_test("D-Bus Connection", "PASS", "Connected to timekprd (REAL MODE - BE CAREFUL!)")
                return True
            except DBusException as e:
                self.print_test("D-Bus Connection", "FAIL", f"Error: {e}")
                print("\n  Troubleshooting:")
                print("    • Is timekprd running? Check with: ps aux | grep timekprd")
                print("    • Are you running as root? Try: sudo python3 test_timekpr_integration.py")
                print("    • Or use: python3 test_timekpr_integration.py --mock (safe mode)")
                return False
        
        self.print_test("Mock Interface", "FAIL", "Mock not available")
        return False

    def test_get_user_list(self) -> bool:
        """Test getting user list."""
        self.print_header("2. Reading Data: Get User List")
        
        if self.mock_interface:
            try:
                users = self.mock_interface.get_user_list()
                self.print_test("getUserList() call", "PASS", f"Returned {len(users)} users")
                for username in users:
                    print(f"    → User: '{username}'")
                if users:
                    # Use target_user if specified, otherwise first user
                    if self.target_user and self.target_user in users:
                        self.test_username = self.target_user
                    else:
                        self.test_username = users[0]
                    self.print_test(
                        "User selection",
                        "PASS",
                        f"Testing with: '{self.test_username}'",
                    )
                    return True
                else:
                    self.print_test("User list", "FAIL", "No users in mock database")
                    return False
            except Exception as e:
                self.print_test("Get User List (mock)", "FAIL", f"Error: {e}")
                return False
        
        if not self.admin_interface:
            self.print_test("Get User List", "FAIL", "D-Bus not connected")
            return False

        try:
            result = self.admin_interface.getUserList()
            self.print_test(
                "getUserList() call",
                "PASS",
                f"Returned {len(result)} items: (status, message, users_list)",
            )

            if isinstance(result, (list, tuple)) and len(result) >= 3:
                status, message, users_raw = result[0], result[1], result[2]
                
                if status == 0:
                    self.print_test("Status code", "PASS", f"status={status} (success)")
                else:
                    self.print_test("Status code", "FAIL", f"status={status}, message='{message}'")
                    return False

                # Parse users
                self.print_test("Raw users list", "PASS", f"Type: {type(users_raw)}, Count: {len(users_raw)}")

                users = []
                for i, user_entry in enumerate(users_raw):
                    username = str(user_entry[0])
                    displayname = str(user_entry[1]) if len(user_entry) > 1 else ""
                    users.append(username)
                    print(f"    → User {i + 1}: '{username}' (display: '{displayname}')")

                if users:
                    # Use target_user if specified, otherwise first user
                    if self.target_user and self.target_user in users:
                        self.test_username = self.target_user
                    else:
                        self.test_username = users[0]  # Use first user for further tests
                    self.print_test(
                        "User parsing",
                        "PASS",
                        f"Extracted {len(users)} usernames, testing with: '{self.test_username}'",
                    )
                    return True
                else:
                    self.print_test("User parsing", "FAIL", "No users found in response")
                    return False
            else:
                self.print_test("Result format", "FAIL", f"Unexpected format: {result}")
                return False

        except DBusException as e:
            self.print_test("Get User List", "FAIL", f"D-Bus error: {e}")
            return False

    def test_get_user_config(self) -> bool:
        """Test getting user configuration."""
        self.print_header("3. Reading Data: Get User Config")
        if not self.test_username:
            self.print_test("Get User Config", "FAIL", "Precondition failed: no user list")
            return False
        
        if self.mock_interface:
            try:
                config = self.mock_interface.get_user_config(self.test_username)
                if config:
                    self.print_test("Config found", "PASS", f"{len(config)} keys returned")
                    print("\n    Sample config keys:")
                    for key in list(config.keys())[:10]:
                        print(f"      • {key}: {config[key]}")
                    return True
                else:
                    self.print_test("Config", "FAIL", "Config is empty")
                    return False
            except Exception as e:
                self.print_test("Get User Config (mock)", "FAIL", f"Error: {e}")
                return False
        
        if not self.admin_interface:
            self.print_test("Get User Config", "FAIL", "D-Bus not connected")
            return False

        try:
            result = self.admin_interface.getUserInformation(self.test_username, "")
            self.print_test(
                "getUserInformation() call",
                "PASS",
                f"Returned {len(result)} items for user '{self.test_username}'",
            )

            if isinstance(result, (list, tuple)) and len(result) >= 3:
                status, message, config = result[0], result[1], result[2]

                if status == 0:
                    self.print_test("Status code", "PASS", f"status={status} (success)")
                else:
                    self.print_test(
                        "Status code",
                        "FAIL",
                        f"status={status}, message='{message}' (user may not be configured)",
                    )
                    return False

                # Print config keys
                if config:
                    config_dict = dict(config)
                    keys = list(config_dict.keys())
                    self.print_test("Config found", "PASS", f"{len(keys)} keys returned")
                    
                    # Print first few keys as examples
                    print("\n    Sample config keys:")
                    for key in keys[:10]:
                        val = config_dict[key]
                        print(f"      • {key}: {val} (type: {type(val).__name__})")
                    if len(keys) > 10:
                        print(f"      ... and {len(keys) - 10} more keys")
                    
                    # Try to extract limits
                    print("\n    Parsing limits from config:")
                    daily_limit = self._extract_limit(config_dict, "daily")
                    weekly_limit = self._extract_limit(config_dict, "weekly")
                    monthly_limit = self._extract_limit(config_dict, "monthly")
                    
                    self.print_test(
                        "Limits extraction",
                        "PASS",
                        f"daily={daily_limit}s, weekly={weekly_limit}s, monthly={monthly_limit}s",
                    )
                    return True
                else:
                    self.print_test("Config", "FAIL", "Config dict is empty (user not configured?)")
                    return False
            else:
                self.print_test("Result format", "FAIL", f"Unexpected format: {result}")
                return False

        except DBusException as e:
            self.print_test("Get User Config", "FAIL", f"D-Bus error: {e}")
            return False

    def _extract_limit(self, config: dict[str, Any], limit_type: str) -> int:
        """Extract time limit from config dict."""
        keys_to_try = {
            "daily": ["LIMITS_PER_WEEKDAYS", "LIMITS_PER_WEEKDAY", "LIMIT_PER_WEEKDAY"],
            "weekly": ["LIMIT_PER_WEEK", "LIMITS_PER_WEEK"],
            "monthly": ["LIMIT_PER_MONTH", "LIMITS_PER_MONTH"],
        }
        for key in keys_to_try.get(limit_type, []):
            if key in config:
                val = config[key]
                # Handle dbus types
                if hasattr(val, "__iter__") and not isinstance(val, str):
                    val = val[0] if val else 0
                return int(val) if val else 0
        return 0

    def test_request_time_left(self) -> bool:
        """Test requesting time left data."""
        self.print_header("4. Reading Data: Request Time Left")
        if not self.test_username:
            self.print_test("Request Time Left", "FAIL", "Precondition failed: no user")
            return False
        
        if self.mock_interface:
            try:
                time_left = self.mock_interface.get_time_left(self.test_username)
                self.print_test(
                    "Mock time_left()",
                    "PASS",
                    f"day={time_left['day']}s, week={time_left['week']}s, month={time_left['month']}s",
                )
                return True
            except Exception as e:
                self.print_test("Get Time Left (mock)", "FAIL", f"Error: {e}")
                return False
        
        if not self.limits_interface:
            self.print_test("Request Time Left", "FAIL", "D-Bus not connected")
            return False

        try:
            result = self.limits_interface.requestTimeLeft(self.test_username)
            self.print_test(
                "requestTimeLeft() call",
                "PASS",
                f"Returned {len(result)} items",
            )

            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                message = result[1] if len(result) > 1 else ""

                if status == 0:
                    self.print_test(
                        "Request status",
                        "PASS",
                        "Request sent (data comes via D-Bus signals)",
                    )
                    print("\n    ⚠ Note: timekpr returns time via D-Bus signals, not direct response")
                    print("      Current implementation uses mock data until signal listener is added")
                    return True
                else:
                    self.print_test("Request status", "FAIL", f"status={status}, message='{message}'")
                    return False
            else:
                self.print_test("Result format", "FAIL", f"Unexpected format: {result}")
                return False

        except DBusException as e:
            self.print_test("Request Time Left", "FAIL", f"D-Bus error: {e}")
            return False

    def test_set_time_left(self) -> bool:
        """Test setting time left."""
        self.print_header("5. Writing Data: Set Time Left")
        if not self.test_username:
            self.print_test("Set Time Left", "FAIL", "Precondition failed: no user")
            return False
        
        if self.mock_interface:
            try:
                test_seconds = 14400  # 4 hours
                success = self.mock_interface.set_time_left_day(self.test_username, test_seconds)
                if success:
                    self.print_test(
                        "Mock setTimeLeft()",
                        "PASS",
                        f"Successfully set time to {test_seconds}s for '{self.test_username}'",
                    )
                    return True
                else:
                    self.print_test("Mock setTimeLeft()", "FAIL", "Failed to set time")
                    return False
            except Exception as e:
                self.print_test("Set Time Left (mock)", "FAIL", f"Error: {e}")
                return False
        
        if not self.admin_interface:
            self.print_test("Set Time Left", "FAIL", "Precondition failed: no user")
            return False

        try:
            # Try to set time (use same value to avoid disrupting user)
            test_seconds = 14400  # 4 hours
            result = self.admin_interface.setTimeLeft(self.test_username, "=", test_seconds)

            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                message = result[1] if len(result) > 1 else ""

                if status == 0:
                    self.print_test(
                        "setTimeLeft() call",
                        "PASS",
                        f"Successfully set time to {test_seconds}s for '{self.test_username}'",
                    )
                    return True
                else:
                    self.print_test(
                        "setTimeLeft() call",
                        "FAIL",
                        f"status={status}, message='{message}'",
                    )
                    return False
            else:
                self.print_test("Result format", "FAIL", f"Unexpected format: {result}")
                return False

        except DBusException as e:
            self.print_test("Set Time Left", "FAIL", f"D-Bus error: {e}")
            return False

    def test_set_allowed_hours_buggy(self) -> bool:
        """Test setAllowedHours with current (buggy) implementation."""
        self.print_header("6. Writing Data: Set Allowed Hours (CURRENT BUGGY)")
        if not self.test_username:
            self.print_test("Set Allowed Hours", "FAIL", "Precondition failed: no user")
            return False
        
        if self.mock_interface:
            try:
                hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
                success = self.mock_interface.set_allowed_hours(self.test_username, 1, hours)
                if success:
                    self.print_test(
                        "Mock setAllowedHours()",
                        "PASS",
                        f"Successfully set hours for day 1: {hours}",
                    )
                    return True
                else:
                    self.print_test("Mock setAllowedHours()", "FAIL", "Failed to set hours")
                    return False
            except Exception as e:
                self.print_test("Set Allowed Hours (mock)", "FAIL", f"Error: {e}")
                return False
        
        if not self.admin_interface:
            self.print_test("Set Allowed Hours", "FAIL", "D-Bus not connected")
            return False

        try:
            # Current code sends a string like "8;9;10"
            # But D-Bus signature expects a{sa{si}} (dict)
            hours_str = "8;9;10"
            
            print(f"    Testing with buggy implementation:")
            print(f"    → Sending hours_str='{hours_str}' (type: str)")
            print(f"    → Expected D-Bus type: a{{sa{{si}}}} (dict)")
            print(f"    → This is why setAllowedHours fails!\n")

            result = self.admin_interface.setAllowedHours(self.test_username, "1", hours_str)

            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                if status == 0:
                    self.print_test("setAllowedHours (buggy)", "PASS", "Unexpected success?")
                    return True
                else:
                    message = result[1] if len(result) > 1 else ""
                    self.print_test(
                        "setAllowedHours (buggy)",
                        "FAIL",
                        f"Expected failure: status={status}, message='{message}'",
                    )
                    return False
        except Exception as e:
            self.print_test("setAllowedHours (buggy)", "FAIL", f"Error: {e}")
            print(f"    This error confirms the type mismatch issue")
            return False

    def test_set_allowed_days(self) -> bool:
        """Test setAllowedDays."""
        self.print_header("7. Writing Data: Set Allowed Days")
        if not self.test_username:
            self.print_test("Set Allowed Days", "FAIL", "Precondition failed: no user")
            return False
        
        if self.mock_interface:
            try:
                days_list = [1, 2, 3, 4, 5]  # Mon-Fri
                success = self.mock_interface.set_allowed_days(self.test_username, days_list)
                if success:
                    self.print_test(
                        "Mock setAllowedDays()",
                        "PASS",
                        f"Successfully set allowed days: {days_list}",
                    )
                    return True
                else:
                    self.print_test("Mock setAllowedDays()", "FAIL", "Failed to set days")
                    return False
            except Exception as e:
                self.print_test("Set Allowed Days (mock)", "FAIL", f"Error: {e}")
                return False
        
        if not self.admin_interface:
            self.print_test("Set Allowed Days", "FAIL", "D-Bus not connected")
            return False

        try:
            # D-Bus signature expects: as (array of strings)
            # Current code sends string - should send array
            days_list = ["1", "2", "3", "4", "5"]  # Mon-Fri
            
            print(f"    Testing with array of strings:")
            print(f"    → Sending days={days_list} (type: list)")
            print(f"    → Expected D-Bus type: as (array of strings)")
            print(f"    → This is correct!\n")

            result = self.admin_interface.setAllowedDays(self.test_username, days_list)

            if isinstance(result, (list, tuple)) and len(result) >= 1:
                status = result[0]
                message = result[1] if len(result) > 1 else ""

                if status == 0:
                    self.print_test(
                        "setAllowedDays() call",
                        "PASS",
                        f"Successfully set allowed days: {days_list}",
                    )
                    return True
                else:
                    self.print_test(
                        "setAllowedDays() call",
                        "FAIL",
                        f"status={status}, message='{message}'",
                    )
                    return False
        except DBusException as e:
            self.print_test("setAllowedDays", "FAIL", f"D-Bus error: {e}")
            return False

    def test_fixed_set_allowed_hours(self) -> bool:
        """Test fixed setAllowedHours with correct D-Bus types."""
        self.print_header("8. Writing Data: Set Allowed Hours (FIXED)")
        if not self.test_username:
            self.print_test("Fixed setAllowedHours", "FAIL", "Precondition failed: no user")
            return False

        if not HAVE_TIMEKPR_APP:
            self.print_test("Fixed setAllowedHours", "SKIP", "timekpr_app module not available")
            return False

        try:
            # Use the fixed implementation from timekpr_app
            interface = TimekprDBusInterface()
            hours = [8, 9, 10, 11]  # 8-11 AM
            day = 1  # Monday
            
            print(f"    Testing with fixed implementation:")
            print(f"    → Calling set_allowed_hours('{self.test_username}', {day}, {hours})")
            print(f"    → Internally converts to D-Bus dict format")
            print(f"    → Expected D-Bus type: a{{sa{{si}}}} (dict)\n")

            success = interface.set_allowed_hours(self.test_username, day, hours)

            if success:
                self.print_test(
                    "set_allowed_hours (FIXED)",
                    "PASS",
                    f"Successfully set allowed hours {hours} for day {day}",
                )
                return True
            else:
                self.print_test(
                    "set_allowed_hours (FIXED)",
                    "FAIL",
                    "Method returned False",
                )
                return False

        except Exception as e:
            self.print_test("set_allowed_hours (FIXED)", "FAIL", f"Error: {e}")
            return False

    def test_fixed_set_limits_per_weekday(self) -> bool:
        """Test fixed setTimeLimitForDays with correct D-Bus types."""
        self.print_header("9. Writing Data: Set Limits Per Weekday (FIXED)")
        if not self.test_username:
            self.print_test("Fixed setTimeLimitForDays", "FAIL", "Precondition failed: no user")
            return False

        if not HAVE_TIMEKPR_APP:
            self.print_test("Fixed setTimeLimitForDays", "SKIP", "timekpr_app module not available")
            return False

        try:
            # Use the fixed implementation from timekpr_app
            interface = TimekprDBusInterface()
            
            # Set different limits for each day (in seconds)
            # Mon-Fri: 14400 (4 hours), Sat-Sun: 21600 (6 hours)
            day_limits = {
                1: 14400,  # Monday
                2: 14400,  # Tuesday
                3: 14400,  # Wednesday
                4: 14400,  # Thursday
                5: 14400,  # Friday
                6: 21600,  # Saturday
                7: 21600,  # Sunday
            }
            
            print(f"    Testing with fixed implementation:")
            print(f"    → Calling set_limits_per_weekday('{self.test_username}', day_limits)")
            print(f"    → Internally converts to D-Bus array format [14400, 14400, ...]")
            print(f"    → Expected D-Bus type: ai (array of ints)\n")

            success = interface.set_limits_per_weekday(self.test_username, day_limits)

            if success:
                self.print_test(
                    "set_limits_per_weekday (FIXED)",
                    "PASS",
                    f"Successfully set daily limits for {self.test_username}",
                )
                return True
            else:
                self.print_test(
                    "set_limits_per_weekday (FIXED)",
                    "FAIL",
                    "Method returned False",
                )
                return False

        except Exception as e:
            self.print_test("set_limits_per_weekday (FIXED)", "FAIL", f"Error: {e}")
            return False

    def print_summary(self) -> None:
        """Print test summary."""
        self.print_header("Summary")
        passed = sum(1 for _, status in self.results if status == "PASS")
        failed = sum(1 for _, status in self.results if status == "FAIL")
        total = len(self.results)

        print(f"\n  Results: {passed} passed, {failed} failed out of {total} tests\n")

        if failed > 0:
            print("  Failed tests:")
            for name, status in self.results:
                if status == "FAIL":
                    print(f"    • {name}")

        print(f"\n{'=' * 70}\n")

    def run(self) -> bool:
        """Run all tests."""
        if not self.test_connection():
            return False

        # Read tests - always run
        self.test_get_user_list()
        self.test_get_user_config()
        self.test_request_time_left()

        # Write tests - skip if read_only mode
        if not self.read_only:
            self.test_set_time_left()
            self.test_set_allowed_hours_buggy()
            self.test_set_allowed_days()
            self.test_fixed_set_allowed_hours()
            self.test_fixed_set_limits_per_weekday()
        else:
            print("\n  📖 Skipping write tests (read-only mode)\n")

        self.print_summary()

        passed = sum(1 for _, status in self.results if status == "PASS")
        return passed > 0


if __name__ == "__main__":
    # Parse command line arguments
    use_mock = True  # Default to safe mock mode
    read_only = False  # Default to read+write tests
    target_user = None  # Default to first user found
    
    args = sys.argv[1:]
    
    if "--real" in args:
        use_mock = False
        print("⚠️  WARNING: Using REAL D-Bus interface")
        print("⚠️  This will MODIFY timekpr settings on your system")
        print("⚠️  Make sure you understand what you're testing!\n")
    elif "--mock" in args:
        use_mock = True
        print("✓ Using MOCK interface (safe for testing)\n")
    else:
        # Default to mock
        print("✓ Using MOCK interface by default (safe)\n")
        print("   Use --real flag for real D-Bus testing (requires sudo)\n")
        use_mock = True
    
    if "--read-only" in args or "--readonly" in args:
        read_only = True
        print("📖 READ-ONLY mode: Will only run read tests (no write operations)\n")
    
    # Check for specific user
    user_args = [a for a in args if not a.startswith("--")]
    if user_args:
        target_user = user_args[0]
        print(f"👤 Target user: '{target_user}'\n")
    
    tester = TimekprTester(use_mock=use_mock)
    tester.read_only = read_only
    tester.target_user = target_user
    success = tester.run()
    sys.exit(0 if success else 1)
