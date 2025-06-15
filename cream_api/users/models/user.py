"""User model definition."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cream_api.db import ModelBase

if TYPE_CHECKING:
    from cream_api.users.models.session import Session


class User(ModelBase):
    """User model representing application users."""

    __tablename__ = "users"

    # Core Fields
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    username: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Account Settings
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Security
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password_reset_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_reset_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    two_factor_secret: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list, nullable=False)

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
