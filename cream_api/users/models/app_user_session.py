"""Session model definition."""

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from whenever import Instant

from cream_api.db import DbModelBase

if TYPE_CHECKING:
    from cream_api.users.models.app_user import AppUser


class AppUserSession(DbModelBase):
    """Session model representing user sessions."""

    __tablename__ = "sessions"

    # Core Fields
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[Instant] = mapped_column(DateTime, default=Instant.now, nullable=False)
    expires_at: Mapped[Instant] = mapped_column(DateTime, nullable=False)
    last_activity: Mapped[Instant] = mapped_column(DateTime, default=Instant.now, nullable=False)

    # Security
    ip_address: Mapped[str] = mapped_column(Text, nullable=False)
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)
    device_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    revoked_at: Mapped[Instant | None] = mapped_column(DateTime, nullable=True)

    # Metadata
    location: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    platform: Mapped[str | None] = mapped_column(Text, nullable=True)
    browser: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    user: Mapped["AppUser"] = relationship("AppUser", back_populates="sessions")
