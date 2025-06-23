"""Custom exceptions for the cream_api package.

This module provides a hierarchy of custom exceptions used throughout the
cream_api package. It includes base exceptions for general errors and
specific exceptions for stock data operations, validation failures, and
not found scenarios.

The exception hierarchy follows a logical structure from general to specific,
allowing for proper error handling and categorization throughout the application.

References:
    - [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)
    - [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""


class CreamException(Exception):
    """Base exception for all cream_api related exceptions.

    This is the root exception class for the cream_api package. All other
    exceptions should inherit from this class to maintain a consistent
    exception hierarchy.
    """


class CreamError(CreamException):
    """Base exception for service related errors.

    This exception serves as the base for all service-level errors in the
    cream_api package. It provides a common interface for error handling
    across different service modules.
    """


class StockDataError(CreamError):
    """Base exception for stock data related errors.

    This exception is raised when errors occur during stock data operations,
    including data retrieval, processing, validation, and storage operations.
    It serves as the parent class for all stock-specific exceptions.
    """


class StockRetrievalError(StockDataError):
    """Exception raised for errors relating to retrieving stock data.

    This exception is raised when there are issues fetching stock data from
    external sources, including network errors, API failures, and data
    parsing problems.
    """


class InvalidStockSymbolError(StockDataError):
    """Exception raised when the stock symbol format is invalid.

    This exception is raised when a stock symbol fails validation checks,
    including format requirements, length constraints, and character restrictions.
    It provides detailed information about why the symbol was rejected.

    Args:
        symbol: The invalid stock symbol that was provided
        reason: A detailed explanation of why the symbol is invalid
    """

    def __init__(self, symbol: str, reason: str):
        """Initialize the exception with the invalid symbol and reason.

        Args:
            symbol: The invalid stock symbol that was provided
            reason: A detailed explanation of why the symbol is invalid
        """
        self.symbol = symbol
        self.reason = reason
        super().__init__(f"Invalid stock symbol '{symbol}': {reason}")


class StockNotFoundError(StockDataError):
    """Exception raised when a stock is not found in the tracking system.

    This exception is raised when attempting to perform operations on a stock
    symbol that is not currently being tracked in the system. This includes
    attempts to deactivate, update, or retrieve data for untracked symbols.

    Args:
        symbol: The stock symbol that was not found in the tracking system
    """

    def __init__(self, symbol: str):
        """Initialize the exception with the symbol that wasn't found.

        Args:
            symbol: The stock symbol that was not found in the tracking system
        """
        self.symbol = symbol
        super().__init__(f"Stock {symbol} is not being tracked")
