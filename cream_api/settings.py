from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database settings
    db_user: str = "creamapp"
    db_password: str = "creamapp"
    db_host: str = "localhost"
    db_name: str = "cream"

    # Admin database settings for migrations
    db_admin_user: str = "postgres"
    db_admin_password: str = "postgres"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_app_config() -> Settings:
    """Returns cached application settings to avoid repeated environment variable lookups."""
    return Settings()
