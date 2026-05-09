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
    
    # Server
    host: str = os.getenv("HOST", "::")
    port: int = int(os.getenv("PORT", "8000"))
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-in-prod!")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    
    # Admin password (hashed with bcrypt)
    admin_password_hash: str = os.getenv(
        "ADMIN_PASSWORD_HASH",
        "$2b$12$9WT/6ve2KeODA3Hm50zAmOLABpFN1IcHiZ7lQEC.otTYP3/YLVexe"  # default: "admin"
    )
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        case_sensitive = False


def get_settings() -> AppSettings:
    """Get application settings (singleton)."""
    return AppSettings()


def get_app_env() -> str:
    """Returner miljønavn."""
    return get_settings().app_env
