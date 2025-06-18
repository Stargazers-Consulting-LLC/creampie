"""File processing functionality for stock data."""

import logging
import os
import shutil

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
        """Process all HTML files in the raw responses directory."""
        for filename in os.listdir(self.config.raw_responses_dir):
            if filename.endswith(".html"):
                file_path = os.path.join(self.config.raw_responses_dir, filename)
                try:
                    await self._process_single_file(file_path)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e!s}")
                    if "Missing required fields" in str(e) or "Failed to parse HTML" in str(e):
                        await self.remove_invalid_file(file_path)
                    else:
                        try:
                            dest_path = os.path.join(self.config.parsed_responses_dir, filename)
                            shutil.move(file_path, dest_path)
                        except Exception as move_error:
                            logger.error(f"Failed to move failed file {file_path}: {move_error!s}")
                    continue

    async def _process_single_file(self, file_path: str) -> None:
        """Process a single HTML file.

        Args:
            file_path: Path to the HTML file to process

        Raises:
            Exception: If file processing fails
        """
        filename = os.path.basename(file_path)
        symbol = filename.split("_")[0]

        data = self.parser.parse_html_file(file_path)
        await self.loader.process_data(symbol, data)

        dest_path = os.path.join(self.config.parsed_responses_dir, filename)
        shutil.move(file_path, dest_path)

    async def process_file_with_error_handling(self, file_path: str) -> bool:
        """Process a single file with error handling.

        Args:
            file_path: Path to the HTML file to process

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            await self._process_single_file(file_path)
            return True
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e!s}")
            try:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.config.parsed_responses_dir, filename)
                shutil.move(file_path, dest_path)
            except Exception as move_error:
                logger.error(f"Failed to move failed file {file_path}: {move_error!s}")
            return False

    async def remove_invalid_file(self, file_path: str) -> None:
        """Remove an invalid file from the raw responses directory.

        Args:
            file_path: Path to the invalid file to remove
        """
        try:
            os.remove(file_path)
            logger.info(f"Removed invalid file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to remove invalid file {file_path}: {e!s}")
