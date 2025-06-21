"""File processing functionality for stock data.

This module provides functionality for processing HTML files containing stock data,
including parsing, validation, and database storage operations.

References:
    - [FastAPI Documentation](https://fastapi.tiangolo.com/)
    - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
    - [Python Type Hints](https://docs.python.org/3/library/typing.html)
    - [PostgreSQL](https://www.postgresql.org/docs/)

### Legal
SPDX-FileCopyright © Robert Ferguson <rmferguson@pm.me>

SPDX-License-Identifier: [MIT](https://spdx.org/licenses/MIT.html)
"""

import logging
import os
import shutil

import psycopg.errors
from stargazer_utils.logging import get_logger_for

from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.parser import StockDataParser

logger: logging.Logger = get_logger_for(__name__)


class FileProcessor:
    """Processor for handling file operations and orchestrating the parsing and loading workflow."""

    def __init__(
        self,
        loader: StockDataLoader,
        config: StockDataConfig | None = None,
    ):
        """Initialize the file processor.

        Args:
            loader: StockDataLoader instance for data processing
            config: StockDataConfig instance (defaults to default config)
        """
        self.loader = loader
        self.config = config or get_stock_data_config()
        self.parser = StockDataParser(config=self.config)

    def _clean_error_message(self, error_msg: str) -> str:
        """Clean error message by removing verbose details.

        Args:
            error_msg: Raw error message

        Returns:
            Cleaned error message
        """
        # Remove the massive parameter dump from the error message
        if "%(id_m" in error_msg:
            parts = error_msg.split("%(id_m")
            if len(parts) > 1:
                error_msg = parts[0].strip()

        return error_msg

    def _move_to_deadletter(self, file_path: str, filename: str) -> None:
        """Move a file to the deadletter directory.

        Args:
            file_path: Path to the file to move
            filename: Name of the file
        """
        deadletter_path = os.path.join(self.config.deadletter_responses_dir, filename)
        try:
            shutil.move(file_path, deadletter_path)
            logger.info(f"Moved to deadletter: {filename}")
        except Exception as move_error:
            logger.error(f"Failed to move {filename}: {type(move_error).__name__}")

    async def process_raw_files(self) -> None:
        """Process all HTML files in the raw responses directory.

        This method orchestrates the complete file processing workflow:
        1. Validates directory contents
        2. Processes each HTML file
        3. Moves successful files to parsed directory
        4. Moves failed files to deadletter directory

        Raises:
            RuntimeError: If non-HTML files are found in raw_responses directory
        """
        all_files = os.listdir(self.config.raw_responses_dir)
        html_files = [f for f in all_files if f.endswith(".html")]
        non_html_files = [f for f in all_files if not f.endswith(".html")]

        # Critical failure: non-HTML files in raw_responses directory
        if non_html_files:
            error_msg = f"CRITICAL: Non-HTML files found in raw_responses directory: {non_html_files}"
            logger.critical(error_msg)
            raise RuntimeError(error_msg)

        if not html_files:
            logger.info("No HTML files found in raw responses directory")
            return

        logger.info(f"Processing {len(html_files)} HTML files")

        for filename in html_files:
            file_path = os.path.join(self.config.raw_responses_dir, filename)
            try:
                symbol = filename.split("_")[0]

                data = self.parser.parse_html_file(file_path)
                logger.info(f"Parsed {len(data.get('prices', []))} price records from {filename}")

                await self.loader.process_data(symbol, data)
                logger.info(f"Successfully processed data for {symbol}")

                parsed_path = os.path.join(self.config.parsed_responses_dir, filename)
                shutil.move(file_path, parsed_path)
                logger.info(f"Processed: {filename}")

            except psycopg.errors.InsufficientPrivilege as e:
                logger.error(f"Database permission error processing {filename}: {type(e).__name__}")
                self._move_to_deadletter(file_path, filename)
            except Exception as e:
                error_msg = self._clean_error_message(str(e))
                logger.error(f"Error processing {filename}: {type(e).__name__}: {error_msg}")
                self._move_to_deadletter(file_path, filename)

        logger.info("File processing completed")

    async def process_single_file(self, file_path: str) -> bool:
        """Process a single HTML file with error handling.

        Args:
            file_path: Path to the HTML file to process

        Returns:
            True if processing was successful, False otherwise
        """
        filename = os.path.basename(file_path)

        try:
            symbol = filename.split("_")[0]

            data = self.parser.parse_html_file(file_path)

            await self.loader.process_data(symbol, data)

            parsed_path = os.path.join(self.config.parsed_responses_dir, filename)
            shutil.move(file_path, parsed_path)
            logger.info(f"Processed: {filename}")
            return True

        except psycopg.errors.InsufficientPrivilege as e:
            logger.error(f"Database permission error processing {filename}: {type(e).__name__}")
            self._move_to_deadletter(file_path, filename)
            return False
        except Exception as e:
            error_msg = self._clean_error_message(str(e))
            logger.error(f"Error processing {filename}: {type(e).__name__}: {error_msg}")
            self._move_to_deadletter(file_path, filename)
            return False

    async def move_to_deadletter(self, file_path: str) -> None:
        """Move a file to the deadletter directory.

        Args:
            file_path: Path to the file to move
        """
        try:
            filename = os.path.basename(file_path)
            deadletter_path = os.path.join(self.config.deadletter_responses_dir, filename)
            shutil.move(file_path, deadletter_path)
            logger.info(f"Moved file to deadletter: {deadletter_path}")
        except Exception as e:
            logger.error(f"Failed to move file {file_path}: {type(e).__name__}: {e!s}")
