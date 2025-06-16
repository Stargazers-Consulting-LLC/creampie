"""Stock data retrieval functionality for Yahoo Finance."""

import asyncio
import logging
from datetime import datetime

import aiohttp
from fastapi import status
from stargazer_utils.logging import get_logger_for

from cream_api.common.exceptions import StockRetrievalError
from cream_api.settings import get_app_settings

settings = get_app_settings()
logger: logging.Logger = get_logger_for(__name__)

BASE_URL = "https://finance.yahoo.com/"
MAX_RETRIES = settings.YAHOO_FINANCE_GET_MAX_RETRIES
RETRY_DELAY = settings.YAHOO_FINANCE_RETRY_DELAY


class StockDataRetriever:
    """Retriever for historical stock data from Yahoo Finance.

    This class handles fetching and saving historical stock data from Yahoo Finance,
    including retry logic for rate limiting and error handling.
    """

    def __init__(self) -> None:
        """Initialize the retriever with required headers."""
        self.headers = {"User-Agent": settings.PARSER_USER_AGENT}
        logger.info(
            "Initialized StockDataRetriever with user agent: %s", settings.PARSER_USER_AGENT
        )

    def save_html(self, symbol: str, html_content: str) -> None:
        """Save HTML content to a file with timestamp.

        Args:
            symbol: Stock symbol to use in filename
            html_content: Raw HTML content to save
        """
        date = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_{date}_{timestamp}.html"
        filepath = settings.HTML_RAW_RESPONSES_DIR / filename

        logger.info("Saving HTML content for symbol %s to file: %s", symbol, filename)
        filepath.write_text(html_content, encoding="utf-8")
        logger.debug("Successfully saved HTML content to %s", filepath)

    async def _handle_response(self, response: aiohttp.ClientResponse, attempt: int) -> str | None:
        """Handle the HTTP response with retry logic for rate limiting.

        Args:
            response: The HTTP response to handle
            attempt: Current attempt number (0-based)

        Returns:
            Response text if successful, None if retry needed

        Raises:
            StockRetrievalError: If the request fails after all retries
        """
        if response.status == status.HTTP_200_OK:
            logger.debug("Received successful response (status 200)")
            return await response.text()
        elif response.status == status.HTTP_429_TOO_MANY_REQUESTS:
            if attempt < MAX_RETRIES - 1:
                logger.warning(
                    "Rate limited (status 429). Attempt %d/%d. Retrying after delay...",
                    attempt + 1,
                    MAX_RETRIES,
                )
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                return None
        logger.error(
            "Request failed with status %d: %s",
            response.status,
            await response.text(),
        )
        raise StockRetrievalError(
            f"Request failed with status {response.status}: {await response.text()}"
        )

    async def _make_request(self, session: aiohttp.ClientSession, url: str) -> str:
        """Make HTTP request with exponential backoff retry mechanism.

        Args:
            session: aiohttp ClientSession for making requests
            url: Complete URL to request

        Returns:
            Response text if successful

        Raises:
            StockRetrievalError: If all retries fail or network error occurs
        """
        for attempt in range(MAX_RETRIES):
            try:
                logger.debug("Making request attempt %d/%d to %s", attempt + 1, MAX_RETRIES, url)
                async with session.get(url, headers=self.headers) as response:
                    if response_text := await self._handle_response(response, attempt):
                        logger.info("Successfully retrieved data on attempt %d", attempt + 1)
                        return response_text
            except aiohttp.ClientError as e:
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                logger.error("Network error after all retries: %s", str(e))
                raise StockRetrievalError(
                    "Network error occurred", f"Failed to connect to Yahoo Finance: {e!s}"
                ) from e

        logger.error("Failed to retrieve data after %d attempts", MAX_RETRIES)
        raise StockRetrievalError(
            "Maximum retries exceeded", f"Failed to retrieve data after {MAX_RETRIES} attempts"
        )

    async def _fetch_page(self, symbol: str, end_timestamp: int) -> str:
        """Fetch historical stock data page from Yahoo Finance.

        Args:
            symbol: Stock symbol to fetch data for
            end_timestamp: Unix timestamp for the end date

        Returns:
            Raw HTML content of the historical data page
        """
        url = f"{BASE_URL}/quote/{symbol}/history/?period1=0&period2={end_timestamp}"
        logger.info(
            "Fetching historical data for symbol %s up to timestamp %d", symbol, end_timestamp
        )

        async with aiohttp.ClientSession() as session:
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
        """
        logger.info("Starting historical data retrieval for symbol %s", symbol)

        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
            logger.debug("Using current date as end date: %s", end_date)

        try:
            end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        except ValueError as e:
            logger.error("Invalid date format provided: %s", end_date)
            raise ValueError(f"Invalid date format: {end_date}. Expected YYYY-MM-DD") from e

        html_content = await self._fetch_page(symbol, end_timestamp)
        self.save_html(symbol, html_content)
        logger.info("Successfully completed historical data retrieval for symbol %s", symbol)
