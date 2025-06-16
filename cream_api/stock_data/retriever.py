"""Stock data retrieval functionality."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from cream_api.settings import get_app_settings
from cream_api.stock_data.data_manager import StockDataManager
from cream_api.stock_data.exceptions import APIError
from cream_api.stock_data.parser import StockDataParser

settings = get_app_settings()

# TODO Refactor this to do what I wanted it to do in the first place
# instead of this weird cache bullshit.


class StockDataRetriever:
    """Retriever for historical stock data from Yahoo Finance."""

    def __init__(self, session: AsyncSession):
        """Initialize the retriever with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.base_url = "https://finance.yahoo.com/"
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        self.headers = {"User-Agent": settings.PARSER_USER_AGENT}
        self.parser = StockDataParser()
        self.manager = StockDataManager(session)
        self.max_retries = settings.PARSER_MAX_RETRIES
        self.retry_delay = settings.PARSER_RETRY_DELAY

    def _get_cache_path(self, symbol: str, date: str) -> Path:
        """Get the cache file path for a symbol and date."""
        return self.cache_dir / f"{symbol}_{date}.html"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file is valid and not expired."""
        if not cache_path.exists():
            return False

        cache_age = datetime.now().timestamp() - cache_path.stat().st_mtime
        return cache_age < settings.CACHE_EXPIRATION_DAYS * 24 * 60 * 60

    async def _make_request(
        self, session: aiohttp.ClientSession, url: str, params: dict[str, Any]
    ) -> str:
        """
        Make HTTP request with retry mechanism.

        Args:
            session: aiohttp ClientSession
            url: Request URL
            params: Query parameters

        Returns:
            Response text

        Raises:
            APIError: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == status.HTTP_200_OK:
                        return await response.text()
                    elif response.status == status.HTTP_429_TOO_MANY_REQUESTS:  # Too Many Requests
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                    raise APIError("", f"Request failed with status {response.status}")
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise APIError("", f"Network error: {e!s}") from e

        raise APIError("", f"Failed after {self.max_retries} retries")

    async def _fetch_page(
        self, symbol: str, start_date: str, end_date: str, offset: int = 0
    ) -> dict[str, Any]:
        """
        Fetch a single page of stock data.

        Args:
            symbol: Stock symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            offset: Page offset for pagination

        Returns:
            Parsed stock data for the page
        """
        # Check cache first
        cache_path = self._get_cache_path(symbol, f"{start_date}_{offset}")
        if self._is_cache_valid(cache_path):
            try:
                html_content = cache_path.read_text(encoding="utf-8")
                return self.parser.parse_html(html_content)
            except Exception:
                pass

        # Construct URL with parameters
        url = f"{self.base_url}/quote/{symbol}/history"
        params = {
            "period1": int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()),
            "period2": int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()),
            "interval": "1d",
            "offset": offset,
        }

        async with aiohttp.ClientSession() as session:
            html_content = await self._make_request(session, url, params)

            # Cache the HTML content
            cache_path.write_text(html_content, encoding="utf-8")

            return self.parser.parse_html(html_content)

    async def _fetch_data(self, symbol: str, start_date: str, end_date: str) -> dict[str, Any]:
        """
        Fetch stock data from Yahoo Finance website with pagination support.

        Args:
            symbol: Stock symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            Combined stock data from all pages

        Raises:
            APIError: If the request fails or returns invalid data
            ValueError: If the date range is invalid
        """
        # Convert dates to timestamps
        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

        # Validate date range
        if start_timestamp > end_timestamp:
            raise ValueError(f"Start date {start_date} is after end date {end_date}")

        # Fetch first page
        all_data = await self._fetch_page(symbol, start_date, end_date)
        offset = 100  # Yahoo Finance typically shows 100 rows per page

        # Fetch additional pages if needed
        while True:
            try:
                page_data = await self._fetch_page(symbol, start_date, end_date, offset)
                if not page_data["prices"]:
                    break
                all_data["prices"].extend(page_data["prices"])
                offset += 100
            except APIError:
                break

        return all_data

    async def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Get historical stock data for a symbol.

        Args:
            symbol: Stock symbol
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format (defaults to today)

        Returns:
            Dictionary containing the parsed stock data

        Raises:
            APIError: If the request fails or returns invalid data
            ValueError: If the date range is invalid
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Fetch and return the data
        return await self._fetch_data(symbol, start_date, end_date)
