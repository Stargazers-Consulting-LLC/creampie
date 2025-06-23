"""Application settings configuration.

This module provides comprehensive application configuration management including
database settings, logging configuration, and environment variable handling.
It uses Pydantic Settings for type-safe configuration with environment file support.

References:
    - [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
    - [Python Logging Documentation](https://docs.python.org/3/library/logging.html)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
import logging.handlers
import os
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this settings file is located
SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(SETTINGS_DIR, ".env")


class Settings(BaseSettings):
    """Configuration for database and frontend integration.

    This class manages all application configuration settings including database
    connection parameters, frontend integration settings, background task configuration,
    and comprehensive logging setup with file rotation support.

    Attributes:
        db_user: Database username for application connections
        db_host: Database host address
        db_name: Database name
        db_password: Database password for application user
        db_admin_user: Database admin username for administrative operations
        db_admin_password: Database admin password
        frontend_url: Frontend application URL for CORS configuration
        enable_background_tasks: Whether to enable background task processing
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None for console-only logging)
        debug_mode: Whether application is running in debug mode
        log_max_size_mb: Maximum log file size in megabytes before rotation
        log_backup_count: Number of backup log files to keep
    """

    # Database configuration
    db_user: str = "creamapp"
    db_host: str = ""
    db_name: str = ""
    db_password: str = ""
    db_admin_user: str = ""
    db_admin_password: str = ""

    # Frontend configuration
    frontend_url: str = ""

    # Background task configuration
    enable_background_tasks: bool = True

    # Logging configuration
    log_level: str = "INFO"
    log_file: str | None = "logs/cream_api.log"
    debug_mode: bool = __debug__
    log_max_size_mb: int = 10
    log_backup_count: int = 5

    def get_connection_string(self) -> str:
        """Get database connection string.

        Returns a database connection string based on configuration settings.
        Falls back to SQLite in-memory database if no database configuration
        is provided.

        Returns:
            str: Database connection string for SQLAlchemy
        """
        if not self.db_host or not self.db_name:
            return "sqlite+aiosqlite:///:memory:"
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH)


app_settings = Settings()


def get_app_settings() -> Settings:
    """Get application configuration settings.

    Returns:
        Settings: Application configuration instance
    """
    return app_settings


def configure_logging(settings: Settings | None = None) -> None:
    """Configure application-wide logging settings.

    This function sets up comprehensive logging configuration including console
    and file handlers with rotation support. It configures different log formats
    for debug and production modes.

    Args:
        settings: Settings instance to use for configuration (defaults to app_settings)

    Raises:
        OSError: If logging file cannot be created or written to
        ValueError: If log level is invalid
    """
    if settings is None:
        settings = app_settings

    log_level = settings.log_level

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if numeric_level is None:
        raise ValueError(f"Invalid log level: {log_level}")

    # Clear any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set formatter based on debug mode
    if settings.debug_mode:
        # Debug format: module_name.thread_id.function_name.line_number.LEVEL-timestamp:\n        message
        log_format = (
            "%(name)s.%(funcName)s.%(lineno)03d.%(levelname)s-%(asctime)s."
            "%(msecs)03d|%(relativeCreated)08d:\n\t%(message)s"
        )
        date_format = "%Y/%m/%d@%H:%M:%S"  # Remove microseconds to avoid formatting issues
    else:
        # Standard format
        log_format = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)

    # Add file handler if specified
    if settings.log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(settings.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Create rotating file handler
        max_bytes = settings.log_max_size_mb * 1024 * 1024  # Convert MB to bytes
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file, maxBytes=max_bytes, backupCount=settings.log_backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)

    # Add console handler
    root_logger.addHandler(console_handler)
    root_logger.setLevel(numeric_level)
