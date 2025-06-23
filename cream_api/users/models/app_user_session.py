"""Session model definition.

This module defines the AppUserSession model for managing user authentication sessions,
including session tracking, security features, and device information. It provides
comprehensive session management capabilities with automatic expiration and activity tracking.

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

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cream_api.db import ModelBase

if TYPE_CHECKING:
    from cream_api.users.models.app_user import AppUser


class AppUserSession(ModelBase):
    """Session model representing user authentication sessions.

    This model provides comprehensive session management capabilities including
    session tracking, security features, device information, and automatic
    expiration handling. It supports session revocation and activity monitoring.

    Attributes:
        id: Unique session identifier
        user_id: Foreign key reference to the associated user
        created_at: Timestamp when the session was created
        expires_at: Timestamp when the session expires
        last_activity: Timestamp of the last activity on this session
        ip_address: IP address from which the session was created
        user_agent: User agent string from the session creation
        device_id: Optional device identifier for multi-device tracking
        is_valid: Whether the session is currently valid
        revoked_at: Timestamp when the session was revoked (if applicable)
        platform: Platform information (e.g., mobile, desktop)
        browser: Browser information for the session
        user: Relationship to the associated AppUser
    """

    __tablename__ = "sessions"

    # Core Fields
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # Security
    ip_address: Mapped[str] = mapped_column(Text, nullable=False)
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)
    device_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Metadata
    platform: Mapped[str | None] = mapped_column(Text, nullable=True)
    browser: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["AppUser"] = relationship("AppUser", back_populates="sessions")
