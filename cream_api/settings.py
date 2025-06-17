"""Application settings configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for database and frontend integration."""

    # Database configuration
    db_user: str = "creamapp"
    db_host: str = ""
    db_name: str = ""
    db_password: str = ""
    db_admin_user: str = ""
    db_admin_password: str = ""

    # Frontend configuration
    frontend_url: str = ""

    # Cache configuration
    CACHE_DIR: Path = Path("files")
    HTML_RAW_RESPONSES_DIR: Path = CACHE_DIR / "raw_responses"

    # Parser configuration
    # Modern Chrome user agent to avoid being blocked by websites
    PARSER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    PARSER_TIMEOUT: int = 30
    YAHOO_FINANCE_GET_MAX_RETRIES: int = 3
    YAHOO_FINANCE_RETRY_DELAY: int = 5

    def get_connection_string(self) -> str:
        """Get database connection string."""
        if not self.db_host or not self.db_name:
            return "sqlite:///:memory:"
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=".env")


app_settings = Settings()


def get_app_settings() -> Settings:
    """Get application configuration settings."""
    return app_settings
