"""Tests for authentication routes."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from cream_api.settings import Settings
from cream_api.users.models.app_user import AppUser
from cream_api.users.routes.auth import get_password_hash


def test_signup_success(client: TestClient, test_db: Session, test_settings: Settings) -> None:
    """Test successful user signup."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "message": "User created successfully. Please contact support to verify your account."
    }

    # Verify user was created in database
    user = test_db.query(AppUser).filter(AppUser.email == "test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert not user.is_verified
    assert user.is_active


def test_signup_duplicate_email(
    client: TestClient, test_db: Session, test_settings: Settings
) -> None:
    """Test signup with existing email."""
    # Create existing user
    user = AppUser(
        email="test@example.com",
        password=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()

    # Try to signup with same email
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Email already registered"}


def test_login_success(client: TestClient, test_db: Session, test_settings: Settings) -> None:
    """Test successful login."""
    # Create verified user
    user = AppUser(
        email="test@example.com",
        password=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()

    # Login
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, test_settings: Settings) -> None:
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}
    assert response.headers.get("www-authenticate") == "Bearer"
