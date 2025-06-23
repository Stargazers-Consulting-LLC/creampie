"""User management functionality for the cream_api package.

This package provides comprehensive user management capabilities including
authentication, session management, and user account operations.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from cream_api.users.models import AppUser, AppUserSession
from cream_api.users.routes.auth import router as auth_router

__all__ = ["AppUser", "AppUserSession", "auth_router"]
