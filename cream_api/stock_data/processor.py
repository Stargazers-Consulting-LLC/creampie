"""File processing functionality for stock data."""

import logging
import shutil
from pathlib import Path

from cream_api.stock_data.config import StockDataConfig, get_stock_data_config
from cream_api.stock_data.loader import StockDataLoader
from cream_api.stock_data.parser import StockDataParser

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Processor for handling file operations and orchestrating the parsing and loading workflow.

    This class is responsible for:
    1. Processing HTML files in the raw responses directory
    2. Orchestrating parsing and loading operations
    3. Managing file movement between directories
    4. Error handling for file processing
    """

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

        For each file:
        1. Parses the HTML content using StockDataParser
        2. Stores the data in the database using StockDataLoader
        3. Moves the file to the parsed responses directory
        4. Handles errors gracefully without stopping the entire process
        """
        # Process each file in the raw directory
        for file_path in self.config.raw_responses_dir.glob("*.html"):
            try:
                await self._process_single_file(file_path)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e!s}")
                # Check if it's an invalid file (missing required fields or parsing error)
                if "Missing required fields" in str(e) or "Failed to parse HTML" in str(e):
                    # Remove invalid files
                    await self.remove_invalid_file(file_path)
                else:
                    # Move other failed files to parsed directory to prevent reprocessing
                    try:
                        shutil.move(str(file_path), str(self.config.parsed_responses_dir / file_path.name))
                    except Exception as move_error:
                        logger.error(f"Failed to move failed file {file_path}: {move_error!s}")
                # Continue processing other files even if one fails
                continue

    async def _process_single_file(self, file_path: Path) -> None:
        """Process a single HTML file.

        Args:
            file_path: Path to the HTML file to process

        Raises:
            Exception: If file processing fails
        """
        # Extract symbol from filename (assuming format: SYMBOL_YYYY-MM-DD.html)
        symbol = file_path.stem.split("_")[0]

        # Parse the HTML file
        data = self.parser.parse_html_file(str(file_path))

        # Process and store the data
        await self.loader.process_data(symbol, data)

        # Move file to parsed directory
        shutil.move(str(file_path), str(self.config.parsed_responses_dir / file_path.name))

    async def process_file_with_error_handling(self, file_path: Path) -> bool:
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
            # Move failed file to parsed directory to prevent reprocessing
            try:
                shutil.move(str(file_path), str(self.config.parsed_responses_dir / file_path.name))
            except Exception as move_error:
                logger.error(f"Failed to move failed file {file_path}: {move_error!s}")
            return False

    async def remove_invalid_file(self, file_path: Path) -> None:
        """Remove an invalid file from the raw responses directory.

        Args:
            file_path: Path to the invalid file to remove
        """
        try:
            file_path.unlink()
            logger.info(f"Removed invalid file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to remove invalid file {file_path}: {e!s}")
