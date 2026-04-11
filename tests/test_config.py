"""Tester for konfigurasjon."""

from mal_prosjekt.config import get_app_env, get_optional_secret


def test_get_app_env_default() -> None:
    assert get_app_env() == "development"


def test_get_optional_secret_missing() -> None:
    assert get_optional_secret("NONEXISTENT_SECRET_XYZ") is None
