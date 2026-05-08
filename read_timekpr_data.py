#!/usr/bin/env python3
"""Safe read-only script to retrieve timekpr data.

This script reads timekpr data directly from files in /var/lib/timekpr/
for reliability. It does NOT use D-Bus signals (which are hard to capture).

Requires: sudo (to read files owned by root)
Usage:
    sudo python3 read_timekpr_data.py                    # Read all users
    sudo python3 read_timekpr_data.py agnes             # Read specific user
    sudo python3 read_timekpr_data.py agnes torgeir     # Read multiple users
"""

import sys

# Import the file-based reader
sys.path.insert(0, '/home/torgeir/prosjekter/timeKpr-app/timeKpr-app/src')
from timekpr_app.timekpr_file import (
    get_timekpr_users,
    get_user_data,
    get_all_users_data,
)


def format_seconds(seconds: int) -> str:
    """Format seconds to human readable string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"


def main():
    print("=" * 70)
    print("TIMEKPR DATA READER (File-based, Read-Only)")
    print("=" * 70)
    print()
    
    # Get target users from command line
    target_users = sys.argv[1:] if len(sys.argv) > 1 else None
    
    try:
        # Get all available users
        all_users = get_timekpr_users()
        
        if not all_users:
            print("✗ No timekpr users found!")
            print()
            print("Troubleshooting:")
            print("  1. Are you running as root? Try: sudo python3 read_timekpr_data.py")
            print("  2. Check if timekpr is configured: ls /var/lib/timekpr/config/")
            return 1
        
        print(f"✓ Found {len(all_users)} configured users")
        print()
        
        # 1. USER LIST
        print("1. USER LIST")
        print("-" * 70)
        for username in all_users:
            print(f"  - {username}")
        print()
        
        # 2. Get data for target users or all users
        if target_users:
            # Filter to only requested users that exist
            target_users = [u for u in target_users if u in all_users]
            if not target_users:
                print(f"⚠ Warning: Requested users not found. Available: {all_users}")
                target_users = all_users
        else:
            target_users = all_users
        
        for username in target_users:
            print(f"2. DATA FOR '{username}'")
            print("-" * 70)
            
            user_data = get_user_data(username)
            
            if user_data:
                # Time limits
                print(f"  Time Limits:")
                print(f"    • Daily:   {user_data.limits.daily}s ({format_seconds(user_data.limits.daily)})")
                print(f"    • Weekly:  {user_data.limits.weekly}s ({format_seconds(user_data.limits.weekly)})")
                print(f"    • Monthly: {user_data.limits.monthly}s ({format_seconds(user_data.limits.monthly)})")
                
                # Consumed time
                print(f"\n  Time Consumed:")
                print(f"    • Today:  {user_data.usage.day}s ({format_seconds(user_data.usage.day)})")
                print(f"    • Week:   {user_data.usage.week}s ({format_seconds(user_data.usage.week)})")
                print(f"    • Month:  {user_data.usage.month}s ({format_seconds(user_data.usage.month)})")
                
                # Remaining time
                print(f"\n  Time Remaining:")
                print(f"    • Today:  {user_data.remaining_day}s ({format_seconds(user_data.remaining_day)})")
                print(f"    • Week:   {user_data.remaining_week}s ({format_seconds(user_data.remaining_week)})")
                print(f"    • Month:  {user_data.remaining_month}s ({format_seconds(user_data.remaining_month)})")
                
                # Allowed days
                day_names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
                day_strs = [day_names.get(d, str(d)) for d in user_data.limits.allowed_weekdays]
                print(f"\n  Allowed Days: {day_strs}")
                
                # Allowed hours (show per day)
                print(f"  Allowed Hours:")
                for day, hours in sorted(user_data.limits.allowed_hours.items()):
                    day_name = day_names.get(day, str(day))
                    print(f"    • {day_name}: {hours}")
                
                # Other settings
                print(f"\n  Settings:")
                print(f"    • Lockout Type: {user_data.limits.lockout_type}")
                print(f"    • Track Inactive: {user_data.limits.track_inactive}")
                print(f"    • Hide Tray Icon: {user_data.limits.hide_tray_icon}")
                
                if user_data.usage.last_checked:
                    print(f"\n  Last Updated: {user_data.usage.last_checked}")
            else:
                print(f"  ✗ Could not read data for {username}")
            
            print()
            print("=" * 70)
            print()
        
        return 0
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
