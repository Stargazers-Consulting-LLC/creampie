"""Custom exceptions for the cream_api package."""


class CreamException(Exception):
    """Base exception for service related exceptions."""


class CreamError(CreamException):
    """Base exception for service related errors."""


class StockDataError(CreamError):
    """Base exception for stock data related errors."""


class StockRetrievalError(StockDataError):
    """Exception raised for errors relating to retrieving stock data."""
