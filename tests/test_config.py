"""Tests for configuration and settings."""

from __future__ import annotations

from timekpr_app.config import get_app_env, get_settings


def test_get_app_env() -> None:
    """Test that app environment is readable."""
    env = get_app_env()
    assert env in ["development", "production"]


def test_get_settings() -> None:
    """Test that settings can be loaded."""
    settings = get_settings()
    assert settings.app_title == "timekpr App"
    assert settings.app_version == "0.1.0"
