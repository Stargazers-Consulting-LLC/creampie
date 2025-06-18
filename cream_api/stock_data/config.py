"""Configuration for stock data module."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class StockDataConfig(BaseModel):
    """Configuration for stock data operations."""

    # File path configuration
    raw_responses_dir: Path = Field(
        default=Path(__file__).parent.parent / "files" / "raw_responses",
        description="Directory for storing raw HTML responses",
    )
    parsed_responses_dir: Path = Field(
        default=Path(__file__).parent.parent / "files" / "parsed_responses",
        description="Directory for storing parsed HTML responses",
    )

    # Parser configuration
    user_agent: str = Field(
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        description="User agent for web requests",
    )
    timeout: int = Field(default=30, description="Timeout for web requests in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries for failed requests")
    retry_delay: int = Field(default=5, description="Delay between retries in seconds")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # Ensure directories exist
        self.raw_responses_dir.mkdir(parents=True, exist_ok=True)
        self.parsed_responses_dir.mkdir(parents=True, exist_ok=True)


# Default configuration instance
default_config = StockDataConfig()


def get_stock_data_config() -> StockDataConfig:
    """Get the default stock data configuration."""
    return default_config


def create_stock_data_config(**kwargs: Any) -> StockDataConfig:
    """Create a custom stock data configuration.

    Args:
        **kwargs: Configuration parameters to override defaults
            - raw_responses_dir: Directory for raw HTML responses
            - parsed_responses_dir: Directory for parsed HTML responses
            - user_agent: User agent for web requests
            - timeout: Timeout for web requests
            - max_retries: Maximum number of retries
            - retry_delay: Delay between retries

    Returns:
        StockDataConfig: Custom configuration instance
    """
    return StockDataConfig(**kwargs)
