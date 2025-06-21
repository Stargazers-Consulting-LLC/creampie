"""Custom exceptions for the cream_api package."""


class CreamException(Exception):
    """Base exception for service related exceptions."""


class CreamError(CreamException):
    """Base exception for service related errors."""


class StockDataError(CreamError):
    """Base exception for stock data related errors."""


class StockRetrievalError(StockDataError):
    """Exception raised for errors relating to retrieving stock data."""


class InvalidStockSymbolError(StockDataError):
    """Exception raised when the stock symbol format is invalid."""

    def __init__(self, symbol: str, reason: str):
        """Initialize the exception with the invalid symbol and reason."""
        self.symbol = symbol
        self.reason = reason
        super().__init__(f"Invalid stock symbol '{symbol}': {reason}")


class StockNotFoundError(StockDataError):
    """Exception raised when a stock is not found in the tracking system."""

    def __init__(self, symbol: str):
        """Initialize the exception with the symbol that wasn't found."""
        self.symbol = symbol
        super().__init__(f"Stock {symbol} is not being tracked")
