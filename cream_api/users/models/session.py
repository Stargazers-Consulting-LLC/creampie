"""Session model definition."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cream_api.db import ModelBase

if TYPE_CHECKING:
    from cream_api.users.models.user import User


class Session(ModelBase):
    """Session model representing user sessions."""

    __tablename__ = "sessions"

    # Core Fields
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Security
    ip_address: Mapped[str] = mapped_column(Text, nullable=False)  # IPv6 compatible
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)
    device_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Metadata
    location: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    platform: Mapped[str | None] = mapped_column(Text, nullable=True)
    browser: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
