"""Database connection and session management."""

from collections.abc import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from cream_api.settings import get_app_settings

settings = get_app_settings()

# Create SQLAlchemy engine
engine = create_engine(settings.get_connection_string(), echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create async engine and session factory
async_engine = create_async_engine(settings.get_connection_string(), echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


class ModelBase(DeclarativeBase):
    """Base class for all database models."""


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
