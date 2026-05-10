#!/usr/bin/env python3
"""Script to check and fix timekpr time for current user.

This script reads timekpr data from files and resets time if needed.
Requires: sudo (to read files owned by root)

Usage:
    sudo python3 fix_timekpr_time.py                    # Check and fix all users
    sudo python3 fix_timekpr_time.py torgeir           # Check and fix specific user
    sudo python3 fix_timekpr_time.py --reset 14400     # Reset to 4 hours for all users with 0 time
    sudo python3 fix_timekpr_time.py torgeir --reset 7200 # Reset torgeir to 2 hours
"""

import sys
import os
import glob

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from timekpr_app.timekpr_file import (
    get_timekpr_users,
    get_user_data,
    TIMEKPR_CONFIG_DIR,
    TIMEKPR_WORK_DIR,
)


def format_seconds(seconds: int) -> str:
    """Format seconds to human readable string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"


def check_and_fix_user(username: str, reset_seconds: int | None = None) -> bool:
    """Check user time and optionally reset if 0."""
    print(f"\n  Checking user: {username}")
    print(f"  {'-' * 50}")
    
    user_data = get_user_data(username)
    
    if user_data is None:
        print(f"  ⚠ User '{username}' not found in timekpr")
        return False
    
    # Show current state
    print(f"  Current remaining time:")
    print(f"    • Today:  {user_data.remaining_day}s ({format_seconds(user_data.remaining_day)})")
    print(f"    • Week:   {user_data.remaining_week}s ({format_seconds(user_data.remaining_week)})")
    print(f"    • Month:  {user_data.remaining_month}s ({format_seconds(user_data.remaining_month)})")
    print(f"  Time consumed today: {user_data.usage.day}s ({format_seconds(user_data.usage.day)})")
    print(f"  Daily limit: {user_data.limits.daily}s ({format_seconds(user_data.limits.daily)})")
    
    # Check if time is 0
    needs_reset = False
    if user_data.remaining_day == 0:
        print(f"  ⚠ Today's time is 0! User may be locked out.")
        needs_reset = True
    
    # If reset requested and time is 0, reset it
    if reset_seconds is not None and needs_reset:
        print(f"  → Resetting daily time to {reset_seconds}s ({format_seconds(reset_seconds)})")
        try:
            from timekpr_app.timekpr import get_timekpr_interface
            interface = get_timekpr_interface()
            success = interface.set_time_left_day(username, reset_seconds)
            if success:
                print(f"  ✓ Successfully reset time for {username}")
                # Verify
                user_data_after = get_user_data(username)
                if user_data_after:
                    print(f"  ✓ Verified: New remaining time = {user_data_after.remaining_day}s ({format_seconds(user_data_after.remaining_day)})")
                return True
            else:
                print(f"  ✗ Failed to reset time for {username}")
                return False
        except Exception as e:
            print(f"  ✗ Error resetting time: {e}")
            return False
    
    if needs_reset and reset_seconds is None:
        print(f"  ℹ Use --reset <seconds> to fix this user")
    
    if not needs_reset:
        print(f"  ✓ User has time remaining, no action needed")
    
    return True


def main():
    print("=" * 70)
    print("TIMEKPR TIME CHECK AND FIX SCRIPT")
    print("=" * 70)
    
    # Parse arguments
    args = sys.argv[1:]
    target_users = []
    reset_seconds = None
    
    for arg in args:
        if arg == "--reset" or arg == "-r":
            # Next arg should be seconds
            pass
        elif arg.isdigit():
            reset_seconds = int(arg)
        elif arg.startswith("--reset="):
            reset_seconds = int(arg.split("=")[1])
        elif not arg.startswith("--"):
            target_users.append(arg)
    
    # Get all users if none specified
    if not target_users:
        all_users = get_timekpr_users()
        if not all_users:
            print("✗ No timekpr users found!")
            print("\nTroubleshooting:")
            print("  • Are you running as root? Try: sudo python3 fix_timekpr_time.py")
            print("  • Check if timekpr is configured: ls /var/lib/timekpr/config/")
            return 1
        target_users = all_users
    
    print(f"\n✓ Found {len(target_users)} user(s) to check")
    print(f"  Users: {', '.join(target_users)}")
    
    if reset_seconds:
        print(f"\n✓ Will reset users with 0 time to {reset_seconds}s ({format_seconds(reset_seconds)})")
    
    print("\n" + "=" * 70)
    print("CHECKING USERS")
    print("=" * 70)
    
    # Check and fix each user
    users_checked = 0
    users_fixed = 0
    users_failed = 0
    
    for username in target_users:
        try:
            fixed = check_and_fix_user(username, reset_seconds)
            users_checked += 1
            if fixed and reset_seconds:
                users_fixed += 1
        except Exception as e:
            print(f"  ✗ Error checking user {username}: {e}")
            users_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Users checked: {users_checked}")
    print(f"  Users fixed:   {users_fixed}")
    print(f"  Errors:        {users_failed}")
    
    if users_fixed > 0:
        print(f"\n✓ Fixed {users_fixed} user(s). Try logging in again.")
    
    if users_failed > 0:
        print(f"\n⚠ {users_failed} user(s) had errors. Check logs above.")
    
    return 0 if users_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
