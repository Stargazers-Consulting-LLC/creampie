"""Tests for authentication routes.

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from cream_api.common.constants import AUTH_LOGIN_PATH, AUTH_SIGNUP_PATH
from cream_api.settings import Settings
from cream_api.users.models.app_user import AppUser
from cream_api.users.routes.auth import get_password_hash


def test_signup_success(client: TestClient, test_db: Session, test_settings: Settings) -> None:
    """Test successful user signup."""
    response = client.post(
        AUTH_SIGNUP_PATH,
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify user was created in database
    user = test_db.query(AppUser).filter(AppUser.email == "test@example.com").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.is_verified
    assert user.is_active


def test_signup_duplicate_email(client: TestClient, test_db: Session, test_settings: Settings) -> None:
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
        AUTH_SIGNUP_PATH,
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
        AUTH_LOGIN_PATH,
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, test_settings: Settings) -> None:
    """Test login with invalid credentials."""
    response = client.post(
        AUTH_LOGIN_PATH,
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}
    assert response.headers.get("www-authenticate") == "Bearer"


def test_login_immediately_after_signup(client: TestClient, test_db: Session, test_settings: Settings) -> None:
    """Test that users can login immediately after signup without email verification."""
    # Signup a new user
    signup_response = client.post(
        AUTH_SIGNUP_PATH,
        json={
            "email": "newuser@example.com",
            "password": "testpassword123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert signup_response.status_code == status.HTTP_201_CREATED

    # Login immediately without email verification
    login_response = client.post(
        AUTH_LOGIN_PATH,
        data={"username": "newuser@example.com", "password": "testpassword123"},
    )
    assert login_response.status_code == status.HTTP_200_OK
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
