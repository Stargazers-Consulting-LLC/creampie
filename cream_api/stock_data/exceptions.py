"""Custom exceptions for stock data functionality."""


class StockDataError(Exception):
    """Base exception for stock data related errors."""


class APIError(StockDataError):
    """Exception raised for API-related errors."""

    def __init__(self, symbol: str, message: str):
        self.symbol = symbol
        super().__init__(f"API error for {symbol}: {message}")


class ValidationError(StockDataError):
    """Exception raised for data validation errors."""

    def __init__(self, symbol: str, errors: list):
        self.symbol = symbol
        self.errors = errors
        error_messages = [f"{e['error']}: {e['details']}" for e in errors]
        super().__init__(f"Validation error for {symbol}:\n" + "\n".join(error_messages))
