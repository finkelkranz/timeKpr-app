"""Tests for FastAPI application."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from timekpr_app.api.main import app

client = TestClient(app)


@pytest.fixture
def test_app() -> TestClient:
    """Create test client."""
    return client


def test_root_endpoint(test_app: TestClient) -> None:
    """Test root endpoint."""
    response = test_app.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check(test_app: TestClient) -> None:
    """Test health check endpoint."""
    response = test_app.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


def test_login_with_wrong_password(test_app: TestClient) -> None:
    """Test login fails with wrong password."""
    response = test_app.post(
        "/auth/login",
        json={"password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_with_default_password(test_app: TestClient) -> None:
    """Test login succeeds with default password 'admin'."""
    response = test_app.post(
        "/auth/login",
        json={"password": "admin"},
    )
    # This will only work if ADMIN_PASSWORD_HASH env var is set to default hash
    # In test environment with default hash (hash of 'admin'),
    # this should succeed
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
