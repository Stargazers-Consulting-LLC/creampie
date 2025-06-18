"""
Common utilities and shared functionality for the cream_api package.
"""

import os

from cream_api.settings import get_app_settings

__all__ = ["get_project_root"]


cfg = get_app_settings()


def get_project_root() -> str:
    """Get the project root directory (creampie)."""
    # Use __name__ for command line scripts without a file
    if __name__ == "__main__":
        # If running as script, get current working directory
        return os.getcwd()
    else:
        # If imported as module, go up from cream_api to project root
        return os.path.dirname(__file__)
