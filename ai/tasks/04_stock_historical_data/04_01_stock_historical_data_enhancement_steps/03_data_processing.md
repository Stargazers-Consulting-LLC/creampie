# Data Processing Implementation Guide

## Data Processor Setup

1. Create `src/data/data_processor.py`:

   ```python
   import logging
   from datetime import datetime
   from typing import Dict, List, Optional

   import pandas as pd
   from dateutil.parser import parse

   logger = logging.getLogger(__name__)

   class DataProcessor:
       def __init__(self):
           self.required_fields = [
               'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume'
           ]

       def process_data(self, raw_data: List[Dict]) -> pd.DataFrame:
           """Process raw stock data into a clean DataFrame."""
           try:
               df = pd.DataFrame(raw_data)
               df = self._clean_data(df)
               df = self._validate_data(df)
               return df
           except Exception as e:
               logger.error(f"Data processing failed: {str(e)}")
               raise DataProcessingError(f"Failed to process data: {str(e)}")
   ```

## Data Cleaning Implementation

1. Implement cleaning methods:

   ```python
   def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
       """Clean and normalize the data."""
       # Ensure all required columns exist
       self._check_required_columns(df)

       # Convert date column to datetime
       df['date'] = pd.to_datetime(df['date'])

       # Remove duplicates
       df = df.drop_duplicates(subset=['date'])

       # Sort by date
       df = df.sort_values('date')

       # Handle missing values
       df = self._handle_missing_values(df)

       # Clean numerical columns
       for col in ['open', 'high', 'low', 'close', 'adj_close']:
           df[col] = self._clean_numerical_column(df[col])

       # Clean volume column
       df['volume'] = self._clean_volume_column(df['volume'])

       return df

   def _check_required_columns(self, df: pd.DataFrame) -> None:
       """Verify all required columns are present."""
       missing_cols = set(self.required_fields) - set(df.columns)
       if missing_cols:
           raise DataProcessingError(f"Missing required columns: {missing_cols}")

   def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
       """Handle missing values in the dataset."""
       # Forward fill missing values for price columns
       price_cols = ['open', 'high', 'low', 'close', 'adj_close']
       df[price_cols] = df[price_cols].fillna(method='ffill')

       # Set volume to 0 for missing values
       df['volume'] = df['volume'].fillna(0)

       return df

   def _clean_numerical_column(self, series: pd.Series) -> pd.Series:
       """Clean numerical columns."""
       # Remove any non-numeric characters
       series = series.replace(r'[^\d.-]', '', regex=True)

       # Convert to float
       series = pd.to_numeric(series, errors='coerce')

       # Replace negative values with NaN
       series = series.where(series >= 0)

       return series

   def _clean_volume_column(self, series: pd.Series) -> pd.Series:
       """Clean volume column."""
       # Remove any non-numeric characters
       series = series.replace(r'[^\d]', '', regex=True)

       # Convert to integer
       series = pd.to_numeric(series, errors='coerce')

       # Replace negative values with 0
       series = series.where(series >= 0, 0)

       return series
   ```

## Data Validation Implementation

1. Implement validation methods:

   ```python
   def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
       """Validate the processed data."""
       # Validate date range
       self._validate_date_range(df)

       # Validate price relationships
       self._validate_price_relationships(df)

       # Validate volume
       self._validate_volume(df)

       # Check for outliers
       self._check_outliers(df)

       return df

   def _validate_date_range(self, df: pd.DataFrame) -> None:
       """Validate the date range of the data."""
       if df['date'].min() < datetime(1900, 1, 1):
           raise DataValidationError("Data contains dates before 1900")

       if df['date'].max() > datetime.now():
           raise DataValidationError("Data contains future dates")

   def _validate_price_relationships(self, df: pd.DataFrame) -> None:
       """Validate relationships between price columns."""
       # High should be >= Open, Close, Low
       invalid_high = (
           (df['high'] < df['open']) |
           (df['high'] < df['close']) |
           (df['high'] < df['low'])
       )

       # Low should be <= Open, Close, High
       invalid_low = (
           (df['low'] > df['open']) |
           (df['low'] > df['close']) |
           (df['low'] > df['high'])
       )

       if invalid_high.any() or invalid_low.any():
           raise DataValidationError("Invalid price relationships detected")

   def _validate_volume(self, df: pd.DataFrame) -> None:
       """Validate volume data."""
       if (df['volume'] < 0).any():
           raise DataValidationError("Negative volume values detected")

   def _check_outliers(self, df: pd.DataFrame) -> None:
       """Check for outliers in the data."""
       for col in ['open', 'high', 'low', 'close', 'adj_close']:
           # Calculate z-scores
           z_scores = (df[col] - df[col].mean()) / df[col].std()

           # Flag values more than 3 standard deviations from mean
           outliers = df[abs(z_scores) > 3]

           if not outliers.empty:
               logger.warning(f"Outliers detected in {col}: {len(outliers)} values")
   ```

## Custom Exceptions

1. Add custom exceptions:

   ```python
   class DataProcessingError(Exception):
       """Base exception for data processing errors."""
       pass

   class DataValidationError(DataProcessingError):
       """Raised when data validation fails."""
       pass
   ```

## Testing

1. Create `tests/test_data_processor.py`:

   ```python
   import pytest
   import pandas as pd
   from datetime import datetime

   from src.data.data_processor import DataProcessor, DataValidationError

   @pytest.fixture
   def sample_data():
       return [
           {
               'date': '2024-01-01',
               'open': 100.0,
               'high': 101.0,
               'low': 99.0,
               'close': 100.5,
               'adj_close': 100.5,
               'volume': 1000000
           }
       ]

   def test_process_data(sample_data):
       processor = DataProcessor()
       df = processor.process_data(sample_data)
       assert isinstance(df, pd.DataFrame)
       assert len(df) == 1
       assert all(col in df.columns for col in processor.required_fields)

   def test_missing_columns():
       processor = DataProcessor()
       with pytest.raises(DataProcessingError):
           processor.process_data([{'date': '2024-01-01'}])

   def test_invalid_price_relationships():
       processor = DataProcessor()
       invalid_data = [{
           'date': '2024-01-01',
           'open': 100.0,
           'high': 90.0,  # Invalid: high < open
           'low': 99.0,
           'close': 100.5,
           'adj_close': 100.5,
           'volume': 1000000
       }]
       with pytest.raises(DataValidationError):
           processor.process_data(invalid_data)
   ```

## Next Steps

After completing the data processing implementation:

1. Run the test suite to verify functionality
2. Test with real stock data
3. Implement database integration
4. Proceed to HTML Caching implementation
