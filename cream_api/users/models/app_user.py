"""User model definition.

This module defines the AppUser model for managing application user accounts,
including authentication, security features, and account settings. It provides
comprehensive user management capabilities with password security and session tracking.

References:
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cream_api.db import ModelBase

if TYPE_CHECKING:
    from cream_api.users.models import AppUserSession


class AppUser(ModelBase):
    """User model representing application user accounts.

    This model provides comprehensive user account management including authentication,
    security features, account settings, and session tracking. It supports password
    security, two-factor authentication, and account verification workflows.

    Attributes:
        id: Unique user identifier
        email: User's email address (used for authentication)
        password: Hashed password for authentication
        first_name: User's first name
        last_name: User's last name
        created_at: Timestamp when the account was created
        updated_at: Timestamp when the account was last updated
        is_verified: Whether the user's email has been verified
        is_active: Whether the user account is active
        last_login: Timestamp of the user's last login
        password_reset_token: Token for password reset functionality
        password_reset_expires: Expiration timestamp for password reset token
        two_factor_enabled: Whether two-factor authentication is enabled
        two_factor_secret: Secret key for two-factor authentication
        sessions: Relationship to user's active sessions
    """

    __tablename__ = "app_users"

    # Core Fields
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Account Settings
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Security
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password_reset_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_reset_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    two_factor_secret: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    sessions: Mapped[list["AppUserSession"]] = relationship(
        "AppUserSession", back_populates="user", cascade="all, delete-orphan"
    )
