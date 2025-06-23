"""Stock data retrieval functionality for Yahoo Finance.

This module provides comprehensive stock data retrieval capabilities from Yahoo Finance,
including HTTP request handling, retry logic, and file storage operations. It handles
asynchronous web scraping with robust error handling and rate limiting support.

References:
    - [aiohttp Documentation](https://docs.aiohttp.org/)
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [Yahoo Finance](https://finance.yahoo.com/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import asyncio
import logging
import os
from datetime import datetime

import aiohttp
from fastapi import status

from cream_api.common.exceptions import StockRetrievalError
from cream_api.stock_data.config import StockDataConfig, get_stock_data_config

logger = logging.getLogger(__name__)

BASE_URL = "https://finance.yahoo.com"
MAX_HEADER_SIZE = 2**32


class StockDataRetriever:
    """Retriever for historical stock data from Yahoo Finance.

    This class provides comprehensive stock data retrieval capabilities from Yahoo Finance,
    including HTTP request handling, retry logic, rate limiting support, and file storage.
    It handles asynchronous web scraping with robust error handling for production use.

    The retriever supports configurable timeouts, retry attempts, and user agent customization
    to ensure reliable data retrieval while respecting rate limits and handling network errors.
    """

    def __init__(self, config: StockDataConfig | None = None) -> None:
        """Initialize the retriever with required headers.

        Args:
            config: StockDataConfig instance (defaults to default config)
        """
        self.config = config or get_stock_data_config()
        self.headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        logger.debug("Initialized StockDataRetriever with user agent: %s", self.config.user_agent)

    def save_html(self, symbol: str, html_content: str) -> None:
        """Save HTML content to a file.

        Args:
            symbol: Stock symbol to use in filename
            html_content: Raw HTML content to save

        Raises:
            OSError: If the file cannot be written to the configured directory
        """
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{symbol}_{date}.html"
        filepath = os.path.join(self.config.raw_responses_dir, filename)

        logger.debug("Saving HTML content for %s to %s", symbol, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
        except OSError as e:
            logger.error("Failed to save HTML content: %s", str(e))
            raise

    async def _handle_response(self, response: aiohttp.ClientResponse, attempt: int) -> str | None:
        """Handle HTTP response with retry logic.

        Args:
            response: The HTTP response to handle
            attempt: Current attempt number (0-based)

        Returns:
            Response text if successful, None if retry needed

        Raises:
            StockRetrievalError: If the request fails after all retries or symbol not found
        """
        if response.status == status.HTTP_200_OK:
            logger.debug("Received successful response (status 200)")
            return await response.text()

        if response.status == status.HTTP_404_NOT_FOUND:
            logger.error("Symbol not found (404)")
            raise StockRetrievalError("Symbol not found", f"Failed to find symbol after {attempt} attempts")

        if response.status == status.HTTP_429_TOO_MANY_REQUESTS:
            logger.warning("Rate limited (429), attempt %d of %d", attempt, self.config.max_retries)
            return None

        logger.error("Unexpected status code %d on attempt %d", response.status, attempt)
        return None

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> str:
        """Make HTTP request with retry logic.

        Args:
            session: aiohttp ClientSession for making requests
            url: Complete URL to request

        Returns:
            Response text if successful

        Raises:
            StockRetrievalError: If all retries fail or network error occurs
        """
        for attempt in range(self.config.max_retries):
            try:
                logger.debug("Request attempt %d/%d to %s", attempt + 1, self.config.max_retries, url)
                async with session.get(url, headers=self.headers) as response:
                    if response_text := await self._handle_response(response, attempt):
                        return response_text
            except aiohttp.ClientError as e:
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                raise StockRetrievalError("Network error occurred", f"Failed to connect to Yahoo Finance: {e!s}") from e

        raise StockRetrievalError(
            "Maximum retries exceeded", f"Failed to retrieve data after {self.config.max_retries} attempts"
        )

    async def _fetch_page(self, symbol: str, end_timestamp: int) -> str:
        """Fetch historical stock data page from Yahoo Finance.

        Args:
            symbol: Stock symbol to fetch data for
            end_timestamp: Unix timestamp for the end date

        Returns:
            Raw HTML content of the historical data page

        Raises:
            StockRetrievalError: If the request fails after all retries
        """
        url = f"{BASE_URL}/quote/{symbol}/history/?period1=0&period2={end_timestamp}"
        logger.info("Fetching historical data for %s up to %d", symbol, end_timestamp)

        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self.headers,
            skip_auto_headers=["Accept-Encoding"],
            max_line_size=MAX_HEADER_SIZE,
            max_field_size=MAX_HEADER_SIZE,
        )
        async with session:
            return await self._make_request(session, url)

    async def get_historical_data(
        self,
        symbol: str,
        end_date: str | None = None,
    ) -> None:
        """Get and save historical stock data for a symbol.

        Args:
            symbol: Stock symbol to fetch data for
            end_date: End date in 'YYYY-MM-DD' format (defaults to today)

        Raises:
            StockRetrievalError: If the request fails after all retries
            ValueError: If the date format is invalid
            OSError: If the HTML content cannot be saved to the configured directory
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        try:
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            raise ValueError(f"Invalid date format: {end_date}. Expected YYYY-MM-DD") from e

        html_content = await self._fetch_page(symbol, end_timestamp)
        self.save_html(symbol, html_content)
        logger.info("Successfully retrieved historical data for %s", symbol)
