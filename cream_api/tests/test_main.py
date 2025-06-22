"""Tests for main application endpoints.

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from fastapi import status
from fastapi.testclient import TestClient

from cream_api.settings import Settings


def test_health_check(client: TestClient, test_settings: Settings) -> None:
    """Test health check endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"app": "root"}
