"""Common pytest fixtures and configuration."""

from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test files."""
    return tmp_path
