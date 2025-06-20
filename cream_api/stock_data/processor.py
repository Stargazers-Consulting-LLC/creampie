"""File processing functionality for stock data."""

import logging
import os
import shutil

import psycopg.errors

from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.parser import StockDataParser

logger = logging.getLogger(__name__)


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

        logger.info(f"Found {len(html_files)} HTML files to process")

        for filename in html_files:
            file_path = os.path.join(self.config.raw_responses_dir, filename)
            try:
                # Extract symbol from filename
                symbol = filename.split("_")[0]

                # Parse HTML file
                data = self.parser.parse_html_file(file_path)

                # Process and store data
                await self.loader.process_data(symbol, data)

                # Move successful file to parsed directory
                parsed_path = os.path.join(self.config.parsed_responses_dir, filename)
                shutil.move(file_path, parsed_path)
                logger.info(f"Successfully processed and moved file: {filename}")

            except psycopg.errors.InsufficientPrivilege as e:
                logger.error(f"Database permission error processing file {file_path}: {e}")
                logger.error("User lacks permission to access sequence stock_data_id_seq")
                logger.error("Please grant USAGE privilege on the sequence or ensure proper database permissions")
                # Move failed file to deadletter directory
                deadletter_path = os.path.join(self.config.deadletter_responses_dir, filename)
                try:
                    shutil.move(file_path, deadletter_path)
                    logger.info(f"Moved failed file to deadletter: {deadletter_path}")
                except Exception as move_error:
                    logger.error(f"Failed to move failed file {file_path}: {move_error!s}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e!s}")
                # Move failed file to deadletter directory
                deadletter_path = os.path.join(self.config.deadletter_responses_dir, filename)
                try:
                    shutil.move(file_path, deadletter_path)
                    logger.info(f"Moved failed file to deadletter: {deadletter_path}")
                except Exception as move_error:
                    logger.error(f"Failed to move failed file {file_path}: {move_error!s}")

    async def process_single_file(self, file_path: str) -> bool:
        """Process a single HTML file with error handling.

        Args:
            file_path: Path to the HTML file to process

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            filename = os.path.basename(file_path)
            symbol = filename.split("_")[0]

            # Parse HTML file
            data = self.parser.parse_html_file(file_path)

            # Process and store data
            await self.loader.process_data(symbol, data)

            # Move successful file to parsed directory
            parsed_path = os.path.join(self.config.parsed_responses_dir, filename)
            shutil.move(file_path, parsed_path)
            logger.info(f"Successfully processed and moved file: {filename}")
            return True

        except psycopg.errors.InsufficientPrivilege as e:
            logger.error(f"Database permission error processing file {file_path}: {e}")
            logger.error("User lacks permission to access sequence stock_data_id_seq")
            logger.error("Please grant USAGE privilege on the sequence or ensure proper database permissions")
            # Move failed file to deadletter directory
            filename = os.path.basename(file_path)
            deadletter_path = os.path.join(self.config.deadletter_responses_dir, filename)
            try:
                shutil.move(file_path, deadletter_path)
                logger.info(f"Moved failed file to deadletter: {deadletter_path}")
            except Exception as move_error:
                logger.error(f"Failed to move failed file {file_path}: {move_error!s}")
            return False
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e!s}")
            # Move failed file to deadletter directory
            filename = os.path.basename(file_path)
            deadletter_path = os.path.join(self.config.deadletter_responses_dir, filename)
            try:
                shutil.move(file_path, deadletter_path)
                logger.info(f"Moved failed file to deadletter: {deadletter_path}")
            except Exception as move_error:
                logger.error(f"Failed to move failed file {file_path}: {move_error!s}")
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
            logger.error(f"Failed to move file {file_path}: {e!s}")
