"""Last konfigurasjon fra miljøvariabler."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Last .env fra prosjektrot hvis den finnes (lokal utvikling)
_root = Path(__file__).resolve().parents[2]
_env = _root / ".env"
if _env.is_file():
    load_dotenv(_env)


class AppSettings(BaseSettings):
    """Applikasjonsinstellinger fra miljøvariabler."""

    app_env: str = os.getenv("APP_ENV", "development")
    app_title: str = "timekpr App"
    app_version: str = "0.1.0"
    
    # Server - CRITICAL: Bind to localhost only for security
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))
    
    # JWT - CRITICAL: Must be set in environment, no defaults
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "15"))
    
    # Admin password - CRITICAL: Must be set in environment, no defaults
    admin_password_hash: str
    
    # Admin username - CRITICAL: Must be set in environment, no defaults
    admin_username: str = "admin"
    
    # CORS - Secure defaults for production
    # CRITICAL: Never use ["*"] with allow_credentials=True
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    
    # CORS - Allowed HTTP methods (restricted to safe methods only)
    cors_allow_methods: list[str] = os.getenv(
        "CORS_ALLOW_METHODS", 
        "GET,POST,PUT,DELETE,OPTIONS,PATCH,HEAD"
    ).split(",")
    
    # CORS - Allowed headers (restricted to necessary headers only)
    cors_allow_headers: list[str] = os.getenv(
        "CORS_ALLOW_HEADERS",
        "Accept,Accept-Language,Content-Language,Content-Type,Authorization"
    ).split(",")
    
    # CORS - Expose headers to browser
    cors_expose_headers: list[str] = os.getenv(
        "CORS_EXPOSE_HEADERS",
        "Content-Length,Content-Range"
    ).split(",")
    
    # CORS - Max age for preflight cache (seconds)
    cors_max_age: int = int(os.getenv("CORS_MAX_AGE", "600"))
    
    # CORS - Allow credentials (cookies, auth headers)
    cors_allow_credentials: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    
    model_config = {"env_file": ".env", "case_sensitive": False}


def get_settings() -> AppSettings:
    """Get application settings (singleton)."""
    return AppSettings()


def get_app_env() -> str:
    """Returner miljønavn."""
    return get_settings().app_env
