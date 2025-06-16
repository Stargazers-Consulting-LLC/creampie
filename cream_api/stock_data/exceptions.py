"""Custom exceptions for stock data functionality."""


class StockDataError(Exception):
    """Base exception for stock data related errors."""


class APIError(StockDataError):
    """Exception raised for API-related errors."""

    def __init__(self, symbol: str, message: str):
        self.symbol = symbol
        super().__init__(f"API error for {symbol}: {message}")
