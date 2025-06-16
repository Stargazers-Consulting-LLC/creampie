# HTML Caching Implementation Guide

## Cache Manager Setup

1. Create `src/cache/html_cache.py`:

   ```python
   import logging
   import os
   from datetime import datetime, timedelta
   from pathlib import Path
   from typing import Optional

   from config.settings import CACHE_SETTINGS, CACHE_DIR

   logger = logging.getLogger(__name__)

   class HTMLCache:
       def __init__(self):
           self.cache_dir = Path(CACHE_DIR)
           self.cache_dir.mkdir(exist_ok=True)
           self.expiration_days = CACHE_SETTINGS['expiration_days']
           self.max_cache_size = CACHE_SETTINGS['max_cache_size']
   ```

## Cache Implementation

1. Implement cache operations:

   ```python
   def get_cache_path(self, symbol: str, date: datetime) -> Path:
       """Get the cache file path for a symbol and date."""
       filename = f"{symbol}_{date.strftime('%Y-%m-%d')}.html"
       return self.cache_dir / filename

   def save_html(self, symbol: str, date: datetime, html: str) -> None:
       """Save HTML content to cache."""
       try:
           cache_path = self.get_cache_path(symbol, date)
           cache_path.write_text(html, encoding='utf-8')
           logger.info(f"Saved HTML cache for {symbol} on {date}")
       except Exception as e:
           logger.error(f"Failed to save HTML cache: {str(e)}")
           raise CacheError(f"Failed to save cache: {str(e)}")

   def get_html(self, symbol: str, date: datetime) -> Optional[str]:
       """Retrieve HTML content from cache."""
       try:
           cache_path = self.get_cache_path(symbol, date)
           if not cache_path.exists():
               return None

           # Check if cache is expired
           if self._is_expired(cache_path):
               cache_path.unlink()
               return None

           # Update last accessed time
           self._update_last_accessed(cache_path)

           return cache_path.read_text(encoding='utf-8')
       except Exception as e:
           logger.error(f"Failed to read HTML cache: {str(e)}")
           return None
   ```

2. Implement cache management:

   ```python
   def _is_expired(self, cache_path: Path) -> bool:
       """Check if cache file is expired."""
       if not cache_path.exists():
           return True

       file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
       expiration_time = datetime.now() - timedelta(days=self.expiration_days)
       return file_time < expiration_time

   def _update_last_accessed(self, cache_path: Path) -> None:
       """Update the last accessed time of a cache file."""
       try:
           os.utime(cache_path, None)
       except Exception as e:
           logger.warning(f"Failed to update last accessed time: {str(e)}")

   def cleanup(self) -> None:
       """Clean up expired and excess cache files."""
       try:
           # Remove expired files
           for cache_file in self.cache_dir.glob("*.html"):
               if self._is_expired(cache_file):
                   cache_file.unlink()
                   logger.info(f"Removed expired cache: {cache_file}")

           # Remove excess files if over limit
           self._enforce_cache_size_limit()
       except Exception as e:
           logger.error(f"Cache cleanup failed: {str(e)}")
           raise CacheError(f"Cache cleanup failed: {str(e)}")

   def _enforce_cache_size_limit(self) -> None:
       """Enforce maximum cache size limit."""
       cache_files = list(self.cache_dir.glob("*.html"))
       if len(cache_files) <= self.max_cache_size:
           return

       # Sort by last accessed time
       cache_files.sort(key=lambda x: x.stat().st_atime)

       # Remove oldest files
       files_to_remove = cache_files[:-self.max_cache_size]
       for file in files_to_remove:
           file.unlink()
           logger.info(f"Removed excess cache: {file}")
   ```

## Cache Index Implementation

1. Create cache index management:

   ```python
   def update_cache_index(self, symbol: str, date: datetime, file_path: Path) -> None:
       """Update the cache index with new file information."""
       try:
           index_path = self.cache_dir / "cache_index.json"
           index = self._load_index(index_path)

           key = f"{symbol}_{date.strftime('%Y-%m-%d')}"
           index[key] = {
               'symbol': symbol,
               'date': date.strftime('%Y-%m-%d'),
               'file_path': str(file_path),
               'last_accessed': datetime.now().isoformat()
           }

           self._save_index(index_path, index)
       except Exception as e:
           logger.error(f"Failed to update cache index: {str(e)}")

   def _load_index(self, index_path: Path) -> dict:
       """Load the cache index."""
       if not index_path.exists():
           return {}

       try:
           import json
           return json.loads(index_path.read_text())
       except Exception as e:
           logger.error(f"Failed to load cache index: {str(e)}")
           return {}

   def _save_index(self, index_path: Path, index: dict) -> None:
       """Save the cache index."""
       try:
           import json
           index_path.write_text(json.dumps(index, indent=2))
       except Exception as e:
           logger.error(f"Failed to save cache index: {str(e)}")
   ```

## Custom Exceptions

1. Add custom exceptions:

   ```python
   class CacheError(Exception):
       """Base exception for cache errors."""
       pass

   class CacheExpiredError(CacheError):
       """Raised when cache is expired."""
       pass

   class CacheFullError(CacheError):
       """Raised when cache is full."""
       pass
   ```

## Testing

1. Create `tests/test_cache.py`:

   ```python
   import pytest
   from datetime import datetime, timedelta
   from pathlib import Path

   from src.cache.html_cache import HTMLCache, CacheError

   @pytest.fixture
   def cache():
       return HTMLCache()

   @pytest.fixture
   def sample_html():
       return "<html><body>Test</body></html>"

   def test_save_and_get_html(cache, sample_html):
       symbol = "AAPL"
       date = datetime.now()
       cache.save_html(symbol, date, sample_html)
       retrieved = cache.get_html(symbol, date)
       assert retrieved == sample_html

   def test_cache_expiration(cache, sample_html):
       symbol = "AAPL"
       date = datetime.now() - timedelta(days=cache.expiration_days + 1)
       cache.save_html(symbol, date, sample_html)
       retrieved = cache.get_html(symbol, date)
       assert retrieved is None

   def test_cache_cleanup(cache, sample_html):
       # Create some test files
       symbol = "AAPL"
       date = datetime.now() - timedelta(days=cache.expiration_days + 1)
       cache.save_html(symbol, date, sample_html)

       # Run cleanup
       cache.cleanup()

       # Verify expired file is removed
       cache_path = cache.get_cache_path(symbol, date)
       assert not cache_path.exists()
   ```

## Next Steps

After completing the HTML caching implementation:

1. Run the test suite to verify functionality
2. Test cache performance with real data
3. Implement database integration
4. Proceed to final integration testing
