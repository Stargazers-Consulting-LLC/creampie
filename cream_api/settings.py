"""Application settings configuration."""

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

    # Background task configuration
    enable_background_tasks: bool = True

    def get_connection_string(self) -> str:
        """Get database connection string."""
        if not self.db_host or not self.db_name:
            return "sqlite+aiosqlite:///:memory:"
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env")


app_settings = Settings()


def get_app_settings() -> Settings:
    """Get application configuration settings."""
    return app_settings
