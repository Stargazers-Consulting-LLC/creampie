"""Authentication routes for user management.

This module provides comprehensive authentication endpoints for user registration,
login, and session management. It includes password hashing, JWT token handling,
and user validation with proper security measures.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [Pydantic Documentation](https://docs.pydantic.dev/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import hashlib
import logging
import secrets
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from cream_api.common.constants import AUTH_PREFIX
from cream_api.db import get_async_db, get_db
from cream_api.users.models.app_user import AppUser

# Router configuration
router = APIRouter(prefix=AUTH_PREFIX, tags=["auth"])

# Security configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Logging configuration
logger = logging.getLogger(__name__)


# Pydantic models for request/response validation
class UserCreate(BaseModel):
    """User registration data model.

    Attributes:
        email: User's email address for account creation
        password: Plain text password (will be hashed)
        first_name: User's first name
        last_name: User's last name
    """

    email: EmailStr
    password: str
    first_name: str
    last_name: str


class Token(BaseModel):
    """JWT token response model.

    Attributes:
        access_token: JWT access token for authentication
        token_type: Type of token (typically "bearer")
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Session token payload model.

    Attributes:
        email: User email from token payload
    """

    email: str | None = None


class TokenPayload(BaseModel):
    """JWT token payload model.

    Attributes:
        sub: Subject identifier (typically user ID or email)
        exp: Token expiration timestamp
    """

    sub: str
    exp: datetime


# Helper functions
def get_password_hash(password: str) -> str:
    """Generate secure password hash using SHA-256 with salt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Salted hash in format "salt$hash"
    """
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validate password against stored hash using the same salt.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash in format "salt$hash"

    Returns:
        bool: True if password matches, False otherwise
    """
    salt, stored_hash = hashed_password.split("$")
    hash_obj = hashlib.sha256((plain_password + salt).encode())
    return hash_obj.hexdigest() == stored_hash


def create_access_token(data: dict) -> str:
    """Create JWT access token.

    Args:
        data: Token payload data

    Returns:
        str: JWT access token

    Note:
        TODO: Implement proper JWT token creation with expiration and signing
    """
    # TODO: Implement proper JWT token creation with expiration and signing
    return "dummy_token"


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]
) -> AppUser:
    """Validate session token and return associated user.

    Args:
        token: JWT token from request
        db: Database session

    Returns:
        AppUser: Authenticated user instance

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = db.query(AppUser).filter(AppUser.password_reset_token == token).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_async(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_async_db)]
) -> AppUser:
    """Validate session token and return associated user (async version).

    Args:
        token: JWT token from request
        db: Async database session

    Returns:
        AppUser: Authenticated user instance

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    stmt = select(AppUser).where(AppUser.password_reset_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


# Route handlers
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=Token)
def signup(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]) -> Token:
    """Create new user account with automatic verification and login.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Token: JWT token for immediate authentication

    Raises:
        HTTPException: If email is already registered
    """
    logger.info(f"Signup request received for email: {user_data.email}")
    logger.info(f"Request data: {user_data}")

    # Check if user already exists
    if db.query(AppUser).filter(AppUser.email == user_data.email).first():
        logger.warning(f"Signup failed - email already registered: {user_data.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = AppUser(
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_verified=True,  # Users are automatically verified
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token for automatic login
    access_token = create_access_token(data={"sub": user_data.email})

    logger.info(f"User created successfully and logged in: {user_data.email}")
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate user and return JWT token.

    Args:
        form_data: OAuth2 password form data
        db: Database session

    Returns:
        Token: JWT token for authentication

    Raises:
        HTTPException: If credentials are invalid
    """
    user = db.query(AppUser).filter(AppUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Email verification is disabled - users can login immediately after signup
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")
