"""Stock data functionality for the cream_api package.

This package provides comprehensive stock data retrieval, processing, and management
capabilities including web scraping, data parsing, and storage operations.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [Pydantic Documentation](https://docs.pydantic.dev/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

from cream_api.stock_data.api import router as stock_data_router
from cream_api.stock_data.config import StockDataConfig, create_stock_data_config, get_stock_data_config

__all__ = ["StockDataConfig", "create_stock_data_config", "get_stock_data_config", "stock_data_router"]
