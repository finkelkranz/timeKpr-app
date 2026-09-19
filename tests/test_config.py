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


def test_cors_defaults() -> None:
    """Test that CORS settings have secure defaults (TOG-20)."""
    settings = get_settings()
    
    # Check CORS origins default
    assert "http://localhost:5173" in settings.cors_origins
    
    # Check CORS methods are restricted (not "*")
    assert "*" not in settings.cors_allow_methods
    assert "GET" in settings.cors_allow_methods
    assert "POST" in settings.cors_allow_methods
    assert "PUT" in settings.cors_allow_methods
    assert "DELETE" in settings.cors_allow_methods
    assert "OPTIONS" in settings.cors_allow_methods
    
    # Check CORS headers are restricted (not "*")
    assert "*" not in settings.cors_allow_headers
    assert "Accept" in settings.cors_allow_headers
    assert "Content-Type" in settings.cors_allow_headers
    assert "Authorization" in settings.cors_allow_headers
    
    # Check CORS credentials default
    assert settings.cors_allow_credentials is True
    
    # Check CORS max age default
    assert settings.cors_max_age == 600
