"""Custom exceptions for the cream_api package."""


class CreamException(Exception):
    """Base exception for service related exceptions."""


class CreamError(CreamException):
    """Base exception for service related errors."""


class StockDataError(CreamError):
    """Base exception for stock data related errors."""


class StockRetrievalError(StockDataError):
    """Exception raised for API-related errors."""

    def __init__(self, symbol: str, message: str):
        self.symbol = symbol
        super().__init__(f"API error for {symbol}: {message}")
