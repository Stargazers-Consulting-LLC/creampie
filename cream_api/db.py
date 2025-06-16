"""Database connection and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .settings import get_app_settings

settings = get_app_settings()

# Create SQLAlchemy engine
engine = create_engine(settings.get_connection_string())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ModelBase(DeclarativeBase):
    """Base class for all database models."""


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
