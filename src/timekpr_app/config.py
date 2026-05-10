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
    
    # CORS - Restrict to specific origins only
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    
    model_config = {"env_file": ".env", "case_sensitive": False}


def get_settings() -> AppSettings:
    """Get application settings (singleton)."""
    return AppSettings()


def get_app_env() -> str:
    """Returner miljønavn."""
    return get_settings().app_env
