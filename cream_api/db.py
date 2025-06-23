"""Database connection and session management.

This module provides comprehensive database connection management including
both synchronous and asynchronous SQLAlchemy engines, session factories,
and dependency injection utilities for FastAPI applications.

References:
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

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
    """Base class for all database models.

    This class serves as the foundation for all SQLAlchemy ORM models in the application.
    It provides the declarative base functionality and ensures consistent model behavior.
    """


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session.

    This function provides a synchronous database session for FastAPI dependency injection.
    It ensures proper session lifecycle management with automatic cleanup.

    Yields:
        Session: SQLAlchemy database session

    Note:
        This is a generator function that yields a session and ensures cleanup
        when the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session.

    This function provides an asynchronous database session for FastAPI dependency injection.
    It ensures proper session lifecycle management with automatic cleanup for async operations.

    Yields:
        AsyncSession: SQLAlchemy async database session

    Note:
        This is an async generator function that yields a session and ensures cleanup
        when the request is complete.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
