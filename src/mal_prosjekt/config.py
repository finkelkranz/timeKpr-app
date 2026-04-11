"""Last konfigurasjon fra miljøvariabler (ikke hardkod hemmeligheter)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Last .env fra prosjektrot hvis den finnes (lokal utvikling)
_root = Path(__file__).resolve().parents[2]
_env = _root / ".env"
if _env.is_file():
    load_dotenv(_env)


def get_app_env() -> str:
    """Returner miljønavn, f.eks. development eller production."""
    return os.getenv("APP_ENV", "development")


def get_optional_secret(name: str) -> str | None:
    """Hent valgfri hemmelighet fra miljø (None hvis ikke satt)."""
    return os.getenv(name)
