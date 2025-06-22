"""Common constants for the Cream API application.

This module contains constants used throughout the application, including
API route prefixes, paths, and other configuration values.

SPDX-FileCopyrightText: 2024 Robert Ferguson <rmferguson@pm.me>
SPDX-License-Identifier: MIT
"""

# API Route Prefixes
API_PREFIX = "/api"
AUTH_PREFIX = "/auth"
STOCK_DATA_PREFIX = "/stock-data"

# Full API Routes
AUTH_BASE_PATH = f"{API_PREFIX}{AUTH_PREFIX}"
STOCK_DATA_BASE_PATH = f"{API_PREFIX}{STOCK_DATA_PREFIX}"

# Specific Endpoints
AUTH_SIGNUP_PATH = f"{AUTH_BASE_PATH}/signup"
AUTH_LOGIN_PATH = f"{AUTH_BASE_PATH}/login"

STOCK_TRACK_PATH = f"{STOCK_DATA_BASE_PATH}/track"
STOCK_TRACKED_PATH = f"{STOCK_DATA_BASE_PATH}/tracked"

# Health Check
HEALTH_CHECK_PATH = "/"
