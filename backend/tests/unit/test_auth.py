# Authentication Unit Tests
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from app.main_stage4 import (
    ALGORITHM,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models_stage1 import User


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_and_verify(self):
        """Test password hashing and verification works correctly."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test access token creation."""
        user_email = "test@ecolehub.be"
        token = create_access_token(data={"sub": user_email})

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 10

    def test_verify_valid_token(self):
        """Test token verification with valid token."""
        user_email = "test@ecolehub.be"
        token = create_access_token(data={"sub": user_email})

        payload = jwt.decode(
            token, "dev-fallback-change-in-production", algorithms=[ALGORITHM]
        )
        assert payload.get("sub") == user_email

    def test_verify_invalid_token(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.jwt.token"

        with pytest.raises(Exception):
            jwt.decode(
                invalid_token,
                "dev-fallback-change-in-production",
                algorithms=[ALGORITHM],
            )


@pytest.mark.auth
class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""

    def test_register_new_user(self, client: TestClient):
        """Test user registration with valid data."""
        user_data = {
            "email": "newuser@ecolehub.be",
            "first_name": "New",
            "last_name": "User",
            "password": "secure123",
        }

        response = client.post("/api/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client: TestClient, test_user_parent: User):
        """Test registration fails with duplicate email."""
        user_data = {
            "email": test_user_parent.email,
            "first_name": "Duplicate",
            "last_name": "User",
            "password": "secure123",
        }

        response = client.post("/api/register", json=user_data)

        assert response.status_code == 400
        assert "déjà enregistré" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test registration fails with invalid email."""
        user_data = {
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User",
            "password": "secure123",
        }

        response = client.post("/api/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_login_valid_credentials(self, client: TestClient, test_user_parent: User):
        """Test login with valid credentials."""
        response = client.post(
            "/api/login",
            data={"email": test_user_parent.email, "password": "jules20220902"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email(self, client: TestClient):
        """Test login fails with non-existent email."""
        response = client.post(
            "/api/login",
            data={"email": "nonexistent@test.be", "password": "jules20220902"},
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client: TestClient, test_user_parent: User):
        """Test login fails with wrong password."""
        response = client.post(
            "/api/login",
            data={"email": test_user_parent.email, "password": "wrongpass"},
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_inactive_user(self, client: TestClient, db_session: Session):
        """Test login fails for inactive user."""
        # Create inactive user
        inactive_user = User(
            email="inactive@test.be",
            first_name="Inactive",
            last_name="User",
            hashed_password=get_password_hash("jules20220902"),
            is_active=False,
        )
        db_session.add(inactive_user)
        db_session.commit()

        response = client.post(
            "/api/login",
            data={"email": "inactive@test.be", "password": "jules20220902"},
        )

        assert response.status_code == 401
        assert "inactif" in response.json()["detail"].lower()

    def test_get_current_user_valid_token(
        self, client: TestClient, auth_headers_parent: dict, test_user_parent: User
    ):
        """Test getting current user info with valid token."""
        response = client.get("/api/me", headers=auth_headers_parent)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "parent@test.be"
        assert data["first_name"] == "Marie"

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user fails without token."""
        response = client.get("/api/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user fails with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/me", headers=headers)

        assert response.status_code == 401
