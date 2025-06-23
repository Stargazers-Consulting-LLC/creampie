"""User routes package for authentication and user management.

This package provides FastAPI route handlers for user authentication,
registration, and session management operations.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from cream_api.users.routes.auth import router as auth_router

__all__ = ["auth_router"]
