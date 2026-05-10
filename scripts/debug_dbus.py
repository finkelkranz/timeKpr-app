#!/usr/bin/env python3
"""Debug script to inspect D-Bus messages from timekprd."""

import dbus
import pprint
from dbus import DBusException

TIMEKPR_DBUS_BUS_NAME = "com.timekpr.server"
TIMEKPR_DBUS_SERVER_PATH = "/com/timekpr/server"
TIMEKPR_DBUS_ADMIN_INTERFACE = "com.timekpr.server.user.admin"
TIMEKPR_DBUS_LIMITS_INTERFACE = "com.timekpr.server.user.limits"


def debug_dbus():
    """Connect to timekprd and inspect what it returns."""
    try:
        bus = dbus.SystemBus()
        proxy = bus.get_object(TIMEKPR_DBUS_BUS_NAME, TIMEKPR_DBUS_SERVER_PATH)
        admin_interface = dbus.Interface(proxy, TIMEKPR_DBUS_ADMIN_INTERFACE)
        
        print("=" * 60)
        print("TIMEKPR D-BUS API INSPECTION")
        print("=" * 60)
        
        # Get introspection to see all methods
        print("\n1. Available methods:")
        print("=" * 60)
        introspect_iface = dbus.Interface(proxy, "org.freedesktop.DBus.Introspectable")
        introspect_xml = introspect_iface.Introspect()
        
        # Parse XML to find methods
        import xml.etree.ElementTree as ET
        root = ET.fromstring(introspect_xml)
        for interface in root.findall('interface'):
            if_name = interface.get('name')
            if "user.admin" in if_name or "user.limits" in if_name:
                print(f"\nInterface: {if_name}")
                for method in interface.findall('method'):
                    method_name = method.get('name')
                    args = []
                    for arg in method.findall('arg'):
                        arg_name = arg.get('name', '')
                        arg_type = arg.get('type', '')
                        direction = arg.get('direction', 'in')
                        args.append(f"{arg_name}({arg_type}, {direction})")
                    print(f"  - {method_name}({', '.join(args)})")
        
        print("\n" + "=" * 60)
        print("2. Trying getUserList():")
        print("=" * 60)
        try:
            result = admin_interface.getUserList()
            print(f"Success! Type: {type(result)}")
            print(f"Value: {result}")
            if isinstance(result, (list, tuple)) and len(result) >= 3:
                status, message, users = result[0], result[1], result[2]
                print(f"\n  status: {status}")
                print(f"  message: {message}")
                print(f"  users: {list(users)}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        print("\n" + "=" * 60)
        print("3. Trying getUserList() - parsing:")
        print("=" * 60)
        try:
            result = admin_interface.getUserList()
            if isinstance(result, (list, tuple)) and len(result) >= 3:
                status, message, users_raw = result[0], result[1], result[2]
                print(f"status: {status} (0 = success)")
                print(f"message: '{message}'")
                print(f"\nRaw users structure: {users_raw}")
                print(f"Type: {type(users_raw)}")
                
                # Parse users list - each entry is [username, displayname]
                users_list = []
                for user_entry in users_raw:
                    if isinstance(user_entry, (list, tuple)) and len(user_entry) >= 1:
                        username = str(user_entry[0])
                        displayname = str(user_entry[1]) if len(user_entry) > 1 else ""
                        users_list.append((username, displayname))
                        print(f"  - {username} (display: '{displayname}')")
                
                # Now try getUserInformation for each user
                print(f"\n4. Trying getUserInformation() for each user:")
                print("=" * 60)
                for username, displayname in users_list:
                    print(f"\nUser: {username} ({displayname})")
                    try:
                        info = admin_interface.getUserInformation(username, "")
                        if isinstance(info, (list, tuple)) and len(info) >= 3:
                            status, message, config = info[0], info[1], info[2]
                            print(f"  status: {status}")
                            print(f"  message: '{message}'")
                            print(f"  config keys: {list(config.keys())}")
                            if config:
                                print(f"  Sample config values:")
                                for k in list(config.keys())[:5]:
                                    v = config[k]
                                    print(f"    {k}: {v} (type: {type(v).__name__})")
                    except Exception as e:
                        print(f"  ERROR: {e}")
        except Exception as e:
            print(f"ERROR parsing getUserList: {e}")
        print("\n" + "=" * 60)
        print("5. Trying requestTimeLeft() on limits interface:")
        print("=" * 60)
        limits_interface = dbus.Interface(proxy, TIMEKPR_DBUS_LIMITS_INTERFACE)
        for username, displayname in users_list:
            print(f"\nUser: {username}")
            try:
                result = limits_interface.requestTimeLeft(username)
                if isinstance(result, (list, tuple)) and len(result) >= 1:
                    status = result[0]
                    message = result[1] if len(result) > 1 else ""
                    print(f"  status: {status}")
                    print(f"  message: '{message}'")
                    print(f"  Full result: {result}")
            except Exception as e:
                print(f"  ERROR: {e}")
        
    except DBusException as e:
        print(f"D-Bus Connection Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is timekprd running? ps aux | grep timekprd")
        print("2. Are you running as root? sudo python3 debug_dbus.py")


if __name__ == "__main__":
    debug_dbus()
