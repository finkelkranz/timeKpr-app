"""SQLite database for storing timekpr statistics history.

This module provides:
- Database initialization
- Storing user statistics snapshots
- Querying historical data

The database is stored in the app's data directory and contains
time series data for all timekpr users.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Database file location
DB_DIR = Path("/var/lib/timekpr-app-data")
DB_FILE = DB_DIR / "stats.db"


def init_db(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Initialize the SQLite database and create tables if they don't exist.
    
    Args:
        db_path: Path to the database file. Uses default if None.
        
    Returns:
        SQLite connection object
    """
    if db_path is None:
        db_path = DB_FILE
    
    # Ensure directory exists
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    # Create tables
    cursor = conn.cursor()
    
    # User statistics history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            time_spent_day INTEGER NOT NULL,
            time_spent_week INTEGER NOT NULL,
            time_spent_month INTEGER NOT NULL,
            remaining_day INTEGER NOT NULL,
            remaining_week INTEGER NOT NULL,
            remaining_month INTEGER NOT NULL,
            daily_limit INTEGER NOT NULL,
            weekly_limit INTEGER NOT NULL,
            monthly_limit INTEGER NOT NULL,
            UNIQUE(username, timestamp)
        )
    """)
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON user_stats_history(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON user_stats_history(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_username_timestamp ON user_stats_history(username, timestamp)")
    
    # Daily summary table (aggregated data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date DATE NOT NULL,
            total_time_spent INTEGER NOT NULL,
            UNIQUE(username, date)
        )
    """)
    
    conn.commit()
    logger.info(f"Database initialized at {db_path}")
    return conn


@contextmanager
def get_db(db_path: str | Path | None = None):
    """Context manager for database connections.
    
    Args:
        db_path: Path to the database file. Uses default if None.
        
    Yields:
        SQLite connection object
    """
    if db_path is None:
        db_path = DB_FILE
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def save_user_stats(user_data: Any, db_path: str | Path | None = None) -> None:
    """Save a snapshot of user statistics to the database.
    
    Args:
        user_data: TimekprUserData object from timekpr_file module
        db_path: Path to the database file
    """
    if db_path is None:
        db_path = DB_FILE
    
    try:
        with get_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_stats_history (
                    username, timestamp, time_spent_day, time_spent_week, 
                    time_spent_month, remaining_day, remaining_week, remaining_month,
                    daily_limit, weekly_limit, monthly_limit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_data.username,
                datetime.now().isoformat(),
                user_data.usage.day,
                user_data.usage.week,
                user_data.usage.month,
                user_data.remaining_day,
                user_data.remaining_week,
                user_data.remaining_month,
                user_data.limits.daily,
                user_data.limits.weekly,
                user_data.limits.monthly,
            ))
            logger.debug(f"Saved stats for {user_data.username}")
    except Exception as e:
        logger.error(f"Failed to save stats for {user_data.username}: {e}")
        raise


def save_all_users_stats(db_path: str | Path | None = None) -> int:
    """Save statistics for all timekpr users.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        Number of users processed
    """
    from timekpr_app.timekpr_file import get_all_users_data
    
    try:
        users_data = get_all_users_data()
        for user_data in users_data:
            save_user_stats(user_data, db_path)
        logger.info(f"Saved stats for {len(users_data)} users")
        return len(users_data)
    except Exception as e:
        logger.error(f"Failed to save all users stats: {e}")
        return 0


def get_user_history(
    username: str,
    days: int = 7,
    db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """Get historical statistics for a user.
    
    Args:
        username: The username to query
        days: Number of days of history to retrieve (default: 7)
        db_path: Path to the database file
        
    Returns:
        List of statistics entries as dictionaries
    """
    if db_path is None:
        db_path = DB_FILE
    
    cutoff = datetime.now() - timedelta(days=days)
    
    try:
        with get_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_stats_history
                WHERE username = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (username, cutoff.isoformat()))
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            
            return results
    except Exception as e:
        logger.error(f"Failed to get history for {username}: {e}")
        return []


def get_daily_usage(
    username: str,
    date: str | None = None,
    db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """Get daily usage statistics for a user.
    
    Args:
        username: The username to query
        date: Specific date (YYYY-MM-DD) or None for today
        db_path: Path to the database file
        
    Returns:
        List of statistics entries for the specified day
    """
    if db_path is None:
        db_path = DB_FILE
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with get_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_stats_history
                WHERE username = ? AND date(timestamp) = ?
                ORDER BY timestamp
            """, (username, date))
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            
            return results
    except Exception as e:
        logger.error(f"Failed to get daily usage for {username} on {date}: {e}")
        return []


def get_weekly_summary(
    username: str,
    db_path: str | Path | None = None
) -> dict[str, Any]:
    """Get weekly summary statistics for a user.
    
    Args:
        username: The username to query
        db_path: Path to the database file
        
    Returns:
        Dictionary with weekly summary statistics
    """
    if db_path is None:
        db_path = DB_FILE
    
    try:
        with get_db(db_path) as conn:
            cursor = conn.cursor()
            
            # Get first entry this week
            cursor.execute("""
                SELECT * FROM user_stats_history
                WHERE username = ? AND date(timestamp) >= date('now', '-7 days')
                ORDER BY timestamp ASC
                LIMIT 1
            """, (username,))
            
            first = cursor.fetchone()
            
            # Get last entry this week
            cursor.execute("""
                SELECT * FROM user_stats_history
                WHERE username = ? AND date(timestamp) >= date('now', '-7 days')
                ORDER BY timestamp DESC
                LIMIT 1
            """, (username,))
            
            last = cursor.fetchone()
            
            if first and last:
                time_spent = last["time_spent_week"] - first["time_spent_week"]
                return {
                    "username": username,
                    "period": "week",
                    "start_time": first["timestamp"],
                    "end_time": last["timestamp"],
                    "time_spent": time_spent,
                    "time_spent_hours": round(time_spent / 3600, 2),
                }
            
            return {
                "username": username,
                "period": "week",
                "error": "No data available",
            }
    except Exception as e:
        logger.error(f"Failed to get weekly summary for {username}: {e}")
        return {"username": username, "error": str(e)}


def get_leaderboard(
    limit: int = 10,
    days: int = 7,
    db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """Get leaderboard of users by time spent (most active).
    
    Args:
        limit: Maximum number of users to return
        days: Number of days to consider
        db_path: Path to the database file
        
    Returns:
        List of user statistics sorted by time spent (descending)
    """
    if db_path is None:
        db_path = DB_FILE
    
    cutoff = datetime.now() - timedelta(days=days)
    
    try:
        with get_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    username,
                    MAX(time_spent_day) as max_daily,
                    AVG(time_spent_day) as avg_daily,
                    SUM(time_spent_day) as total_spent,
                    COUNT(*) as readings
                FROM user_stats_history
                WHERE timestamp >= ?
                GROUP BY username
                ORDER BY total_spent DESC
                LIMIT ?
            """, (cutoff.isoformat(), limit))
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            
            return results
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}")
        return []


def cleanup_old_data(
    max_age_days: int = 90,
    db_path: str | Path | None = None
) -> int:
    """Remove old statistics data.
    
    Args:
        max_age_days: Maximum age of data to keep (default: 90 days)
        db_path: Path to the database file
        
    Returns:
        Number of rows deleted
    """
    if db_path is None:
        db_path = DB_FILE
    
    cutoff = datetime.now() - timedelta(days=max_age_days)
    
    try:
        with get_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM user_stats_history
                WHERE timestamp < ?
            """, (cutoff.isoformat(),))
            
            deleted = cursor.rowcount
            logger.info(f"Cleaned up {deleted} old records")
            return deleted
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        return 0
