"""Application settings configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for database and frontend integration."""

    # Database configuration
    db_user: str = "creamapp"
    db_host: str = ""
    db_name: str = ""
    db_url: str = ""
    db_password: str = ""
    db_admin_user: str = ""
    db_admin_password: str = ""

    # Frontend configuration
    frontend_url: str = ""

    model_config = SettingsConfigDict(env_file=".env")


app_settings = Settings()


def get_app_settings() -> Settings:
    """Get application configuration settings."""
    return app_settings
