"""Configuration for stock data module.

This module provides configuration management for stock data operations including
web scraping settings, file storage directories, and retry logic.

References:
    - [Pydantic Documentation](https://docs.pydantic.dev/)
    - [Python os.path Documentation](https://docs.python.org/3/library/os.path.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import os
from typing import Any

from pydantic import BaseModel, Field

from cream_api.common import get_project_root

__all__ = [
    "StockDataConfig",
    "create_stock_data_config",
    "get_stock_data_config",
]


class StockDataConfig(BaseModel):
    """Configuration for stock data operations.

    This class manages all configuration settings for stock data retrieval,
    including file storage directories, web request settings, and retry logic.
    Directories are automatically created when the configuration is instantiated.

    You probably want to use the `get_stock_data_config` function to get
    a configuration instance instead.

    Attributes:
        raw_responses_dir: Directory for storing raw HTML responses
        parsed_responses_dir: Directory for storing parsed HTML responses
        deadletter_responses_dir: Directory for storing failed HTML responses
        user_agent: User agent string for web requests
        timeout: Timeout for web requests in seconds
        max_retries: Maximum number of retries for failed requests
        retry_delay: Delay between retries in seconds
    """

    raw_responses_dir: str = Field(
        default=os.path.join(get_project_root(), "stock_data", "files", "raw_responses"),
        description="Directory for storing raw HTML responses",
    )
    parsed_responses_dir: str = Field(
        default=os.path.join(get_project_root(), "stock_data", "files", "parsed_responses"),
        description="Directory for storing parsed HTML responses",
    )
    deadletter_responses_dir: str = Field(
        default=os.path.join(get_project_root(), "stock_data", "files", "deadletter_responses"),
        description="Directory for storing failed HTML responses",
    )

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
        """Initialize configuration and create required directories.

        Args:
            **data: Configuration data to override defaults
        """
        super().__init__(**data)
        os.makedirs(self.raw_responses_dir, exist_ok=True)
        os.makedirs(self.parsed_responses_dir, exist_ok=True)
        os.makedirs(self.deadletter_responses_dir, exist_ok=True)


default_config = StockDataConfig()


def get_stock_data_config() -> StockDataConfig:
    """Get the default stock data configuration.

    Returns:
        StockDataConfig: The default configuration instance
    """
    return default_config


def create_stock_data_config(**kwargs: Any) -> StockDataConfig:
    """Create a custom stock data configuration.

    Args:
        **kwargs: Configuration parameters to override defaults
            - raw_responses_dir: Directory for raw HTML responses
            - parsed_responses_dir: Directory for parsed HTML responses
            - deadletter_responses_dir: Directory for failed HTML responses
            - user_agent: User agent for web requests
            - timeout: Timeout for web requests
            - max_retries: Maximum number of retries
            - retry_delay: Delay between retries

    Returns:
        StockDataConfig: Custom configuration instance
    """
    return StockDataConfig(**kwargs)
