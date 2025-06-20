"""Common utilities and shared functionality for the cream_api package."""

import os

from cream_api.settings import get_app_settings

__all__ = ["get_project_root"]

app_settings = get_app_settings()


def get_project_root() -> str:
    """Get the project root directory (creampie)."""
    if __name__ == "__main__":
        return os.getcwd()
    else:
        current_file = os.path.abspath(__file__)
        working_dir = os.path.abspath(os.getcwd())
        return os.path.commonpath([current_file, working_dir])
