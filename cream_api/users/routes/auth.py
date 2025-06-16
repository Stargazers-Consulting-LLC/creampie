"""Authentication routes for user management."""

import hashlib
import secrets
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from cream_api.db import get_db
from cream_api.users.models.app_user import AppUser

# Router configuration
router = APIRouter(prefix="/auth", tags=["auth"])

# Security configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Pydantic models for request/response validation
class UserCreate(BaseModel):
    """User registration data model."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Session token payload model."""

    email: str | None = None


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str
    exp: datetime


# Helper functions
def get_password_hash(password: str) -> str:
    """Using SHA-256 with salt for secure password storage."""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validates password against stored hash using the same salt."""
    salt, stored_hash = hashed_password.split("$")
    hash_obj = hashlib.sha256((plain_password + salt).encode())
    return hash_obj.hexdigest() == stored_hash


def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    # TODO: Implement proper JWT token creation
    return "dummy_token"


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]
) -> AppUser:
    """Validates session token and returns associated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = db.query(AppUser).filter(AppUser.password_reset_token == token).first()
    if user is None:
        raise credentials_exception
    return user


# Route handlers
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]) -> dict:
    """Creates new user account with manual verification requirement."""
    # Check if user already exists
    if db.query(AppUser).filter(AppUser.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = AppUser(
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_verified=False,
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully."}


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate user and return JWT token."""
    user = db.query(AppUser).filter(AppUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email before logging in",
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")
