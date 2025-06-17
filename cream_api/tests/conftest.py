"""Test configuration and fixtures."""

from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from cream_api.db import ModelBase, get_async_db, get_db
from cream_api.main import app
from cream_api.settings import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Test settings with in-memory SQLite database."""
    return Settings(
        db_user="test",
        db_host="localhost",
        db_name="test",
        db_password="test",
        db_admin_user="test",
        db_admin_password="test",
        frontend_url="http://localhost:5173",
    )


@pytest.fixture
def test_db(test_settings: Settings) -> Generator[Session, None, None]:
    """Create a test database session."""
    # Create SQLite in-memory database URL
    test_db_url = "sqlite:///:memory:"

    # Create engine with SQLite
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create session factory
    test_sess_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    ModelBase.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = test_sess_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield test_sess_local()

    # Clean up by dropping all tables
    ModelBase.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture
async def async_test_db(test_settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    """Create an async test database session."""
    # Create SQLite in-memory database URL for async
    test_db_url = "sqlite+aiosqlite:///:memory:"

    # Create async engine
    engine = create_async_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create async session factory
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)

    # Override the get_async_db dependency
    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_async_db] = override_get_async_db

    # Create and yield session
    async with async_session() as session:
        yield session

    # Clean up by dropping all tables
    async with engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)


@pytest.fixture
def client(test_db: Session) -> TestClient:
    """Create a test client with the test database."""
    return TestClient(app)


@pytest.fixture
def async_client(async_test_db: AsyncSession) -> TestClient:
    """Create a test client with the async test database."""
    return TestClient(app)
