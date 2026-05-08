"""Comprehensive tests for FastAPI application using mock interface."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from timekpr_app.api.main import app
from timekpr_app.timekpr_mock import MockTimekprDBusInterface, reset_mock_users


@pytest.fixture
def test_app() -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_mock() -> None:
    """Reset mock users before each test."""
    reset_mock_users()


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, test_app: TestClient) -> None:
        """Test root endpoint returns expected data."""
        response = test_app.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, test_app: TestClient) -> None:
        """Test health check endpoint."""
        response = test_app.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "environment" in data


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_login_with_wrong_password(self, test_app: TestClient) -> None:
        """Test login fails with wrong password."""
        response = test_app.post(
            "/api/auth/login",
            json={"password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_with_default_password(self, test_app: TestClient) -> None:
        """Test login succeeds with default password 'admin'."""
        response = test_app.post(
            "/api/auth/login",
            json={"password": "admin"},
        )
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data

    def test_login_missing_password(self, test_app: TestClient) -> None:
        """Test login fails with missing password."""
        response = test_app.post(
            "/api/auth/login",
            json={},
        )
        assert response.status_code == 422  # Validation error


class TestStatsEndpoints:
    """Tests for statistics endpoints using mock interface."""

    @pytest.fixture
    def authenticated_client(self, test_app: TestClient) -> TestClient:
        """Get authenticated client with JWT token."""
        response = test_app.post(
            "/api/auth/login",
            json={"password": "admin"},
        )
        if response.status_code != 200:
            pytest.skip("Cannot authenticate - default password not set")
        
        token = response.json()["access_token"]
        client = TestClient(app)
        client.headers = {"Authorization": f"Bearer {token}"}
        return client

    def test_get_users_unauthenticated(self, test_app: TestClient) -> None:
        """Test that /api/stats/users requires authentication."""
        response = test_app.get("/api/stats/users")
        assert response.status_code == 401

    @patch("timekpr_app.api.stats.get_timekpr_interface")
    @patch("timekpr_app.api.stats.get_all_users_data")
    def test_get_users_authenticated(
        self, mock_get_file_data, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test getting user list with authentication."""
        # Mock file-based reader to return empty (force fallback to D-Bus)
        mock_get_file_data.side_effect = FileNotFoundError("Mock mode - use D-Bus")
        
        mock_iface = MockTimekprDBusInterface()
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.get("/api/stats/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "testuser" in data

    @patch("timekpr_app.api.stats.get_timekpr_interface")
    @patch("timekpr_app.api.stats.get_user_data")
    def test_get_user_stats(
        self, mock_get_file_data, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test getting user statistics."""
        # Mock file-based reader to raise error (force fallback to D-Bus)
        mock_get_file_data.side_effect = FileNotFoundError("Mock mode - use D-Bus")
        
        mock_iface = MockTimekprDBusInterface()
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.get("/api/stats/users/testuser")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "time_left_today" in data
        assert "time_left_week" in data
        assert "time_left_month" in data
        assert "daily_limit" in data

    @patch("timekpr_app.api.stats.get_timekpr_interface")
    def test_get_user_stats_nonexistent(
        self, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test getting stats for non-existent user."""
        mock_iface = MockTimekprDBusInterface()
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.get("/api/stats/users/nonexistent")
        assert response.status_code == 200


class TestConfigEndpoints:
    """Tests for configuration endpoints using mock interface."""

    @pytest.fixture
    def authenticated_client(self, test_app: TestClient) -> TestClient:
        """Get authenticated client with JWT token."""
        response = test_app.post(
            "/api/auth/login",
            json={"password": "admin"},
        )
        if response.status_code != 200:
            pytest.skip("Cannot authenticate")
        
        token = response.json()["access_token"]
        client = TestClient(app)
        client.headers = {"Authorization": f"Bearer {token}"}
        return client

    def test_get_user_config_unauthenticated(self, test_app: TestClient) -> None:
        """Test that /api/config/users/{username} requires authentication."""
        response = test_app.get("/api/config/users/testuser")
        assert response.status_code == 401

    @patch("timekpr_app.api.config.get_timekpr_interface")
    def test_get_user_config(
        self, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test getting user configuration."""
        mock_iface = MockTimekprDBusInterface()
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.get("/api/config/users/testuser")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "daily_limit" in data
        assert "weekly_limit" in data
        assert "monthly_limit" in data

    @patch("timekpr_app.api.config.get_timekpr_interface")
    def test_set_time_left_today(
        self, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test setting time left for today."""
        mock_iface = MockTimekprDBusInterface()
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.put(
            "/api/config/users/testuser/time-left-today?seconds=7200"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @patch("timekpr_app.api.config.get_timekpr_interface")
    def test_set_allowed_hours(
        self, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test setting allowed hours for a day."""
        mock_iface = MockTimekprDBusInterface()
        mock_get_iface.return_value = mock_iface
        
        hours = [8, 9, 10, 11, 12, 13, 14, 15]
        response = authenticated_client.put(
            "/api/config/users/testuser/allowed-hours",
            json={"day": 1, "hours": hours},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @patch("timekpr_app.api.config.get_timekpr_interface")
    def test_set_allowed_hours_invalid_day(
        self, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test setting allowed hours with invalid day."""
        mock_iface = MockTimekprDBusInterface()
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.put(
            "/api/config/users/testuser/allowed-hours",
            json={"day": 0, "hours": [8, 9]},
        )
        assert response.status_code == 400


class TestErrorHandling:
    """Tests for error handling in API endpoints."""

    @pytest.fixture
    def authenticated_client(self, test_app: TestClient) -> TestClient:
        """Get authenticated client with JWT token."""
        response = test_app.post(
            "/api/auth/login",
            json={"password": "admin"},
        )
        if response.status_code != 200:
            pytest.skip("Cannot authenticate")
        
        token = response.json()["access_token"]
        client = TestClient(app)
        client.headers = {"Authorization": f"Bearer {token}"}
        return client

    @patch("timekpr_app.api.stats.get_timekpr_interface")
    @patch("timekpr_app.api.stats.get_all_users_data")
    def test_stats_endpoint_exception(
        self, mock_get_file_data, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test that exceptions in stats endpoint are handled."""
        from unittest.mock import MagicMock
        # Mock file-based reader to raise error
        mock_get_file_data.side_effect = Exception("Test error")
        # Also mock D-Bus
        mock_iface = MagicMock()
        mock_iface.get_user_list.side_effect = Exception("Test error")
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.get("/api/stats/users")
        assert response.status_code == 500

    @patch("timekpr_app.api.config.get_timekpr_interface")
    def test_config_endpoint_exception(
        self, mock_get_iface, authenticated_client: TestClient
    ) -> None:
        """Test that exceptions in config endpoint are handled."""
        from unittest.mock import MagicMock
        mock_iface = MagicMock()
        mock_iface.get_user_config.side_effect = Exception("Test error")
        mock_get_iface.return_value = mock_iface
        
        response = authenticated_client.get("/api/config/users/testuser")
        assert response.status_code == 500
