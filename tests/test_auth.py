"""Tests for authentication."""

from __future__ import annotations

from timekpr_app.auth import hash_password, verify_password


def test_hash_password_creates_different_hashes() -> None:
    """Test that hashing the same password produces different hashes."""
    password = "test123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2  # bcrypt adds random salt


def test_verify_password_correct() -> None:
    """Test that correct password verifies successfully."""
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)


def test_verify_password_incorrect() -> None:
    """Test that incorrect password fails verification."""
    password = "test123"
    hashed = hash_password(password)
    assert not verify_password("wrongpassword", hashed)
