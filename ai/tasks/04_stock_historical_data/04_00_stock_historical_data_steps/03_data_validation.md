# Step 3: Data Validation Implementation

## Overview

In this step, we'll implement data validation to ensure the quality and completeness of stock data before storing it in the database.

## Tasks

### 1. Create Data Validator

In `cream_api/stock_data/validator.py`:

```python
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

class StockDataValidator:
    def __init__(self):
        self.required_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

    async def validate_data(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Validate stock data for quality and completeness.

        Args:
            data (pd.DataFrame): Stock data to validate

        Returns:
            List[Dict[str, Any]]: List of validation errors, empty if data is valid
        """
        errors = []

        # Check if data is empty
        if data.empty:
            errors.append({
                'error': 'No data received',
                'details': 'The API returned an empty dataset'
            })
            return errors

        # Check required columns
        missing_columns = [col for col in self.required_columns if col not in data.columns]
        if missing_columns:
            errors.append({
                'error': 'Missing required columns',
                'details': f'Missing columns: {", ".join(missing_columns)}'
            })
            return errors

        # Check for missing values
        for column in self.required_columns:
            if data[column].isnull().any():
                errors.append({
                    'error': 'Missing values detected',
                    'details': f'Column {column} contains null values'
                })

        # Check price consistency
        price_errors = data[
            (data['High'] < data['Low']) |
            (data['Open'] < data['Low']) |
            (data['Open'] > data['High']) |
            (data['Close'] < data['Low']) |
            (data['Close'] > data['High'])
        ]
        if not price_errors.empty:
            errors.append({
                'error': 'Price inconsistency detected',
                'details': f'Found {len(price_errors)} rows with invalid price relationships'
            })

        # Check for negative volume
        if (data['Volume'] < 0).any():
            errors.append({
                'error': 'Invalid volume detected',
                'details': 'Found negative volume values'
            })

        # Check date order
        if not data.index.is_monotonic_increasing:
            errors.append({
                'error': 'Date order issue',
                'details': 'Dates are not in chronological order'
            })

        # Check for future dates
        today = pd.Timestamp.now().normalize()
        future_dates = data[data.index > today]
        if not future_dates.empty:
            errors.append({
                'error': 'Future dates detected',
                'details': f'Found {len(future_dates)} dates in the future'
            })

        return errors
```

### 2. Update Data Retriever

In `cream_api/stock_data/retriever.py`, update the `get_historical_data` method:

```python
from .validator import StockDataValidator

class StockDataRetriever:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.validator = StockDataValidator()

    async def get_historical_data(self, symbol: str, start_date: str, end_date: Optional[str] = None) -> None:
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        try:
            # Fetch data from API
            raw_data = await self._fetch_data(symbol, start_date, end_date)
            data = self._process_response(raw_data)

            # Validate data
            errors = await self.validator.validate_data(data)
            if errors:
                error_messages = [f"{e['error']}: {e['details']}" for e in errors]
                raise ValueError(f"Data validation failed for {symbol}:\n" + "\n".join(error_messages))

            # Convert data to database models
            for date, row in data.iterrows():
                stock_data = StockData(
                    symbol=symbol,
                    date=date,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    adj_close=float(row['Adj Close']),
                    volume=int(row['Volume'])
                )
                self.session.add(stock_data)

            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Error retrieving data for {symbol}: {str(e)}")
```

### 3. Create Tests

In `cream_api/tests/stock_data/test_validator.py`:

```python
import pytest
import pandas as pd
from datetime import datetime, timedelta
from cream_api.stock_data.validator import StockDataValidator

@pytest.mark.asyncio
async def test_validate_valid_data():
    validator = StockDataValidator()

    # Create valid test data
    dates = pd.date_range(start='2023-01-01', end='2023-01-05')
    data = pd.DataFrame({
        'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'High': [105.0, 106.0, 107.0, 108.0, 109.0],
        'Low': [95.0, 96.0, 97.0, 98.0, 99.0],
        'Close': [102.0, 103.0, 104.0, 105.0, 106.0],
        'Adj Close': [102.0, 103.0, 104.0, 105.0, 106.0],
        'Volume': [1000, 1100, 1200, 1300, 1400]
    }, index=dates)

    errors = await validator.validate_data(data)
    assert len(errors) == 0

@pytest.mark.asyncio
async def test_validate_invalid_data():
    validator = StockDataValidator()

    # Create invalid test data
    dates = pd.date_range(start='2023-01-01', end='2023-01-05')
    data = pd.DataFrame({
        'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'High': [95.0, 96.0, 97.0, 98.0, 99.0],  # High < Low
        'Low': [105.0, 106.0, 107.0, 108.0, 109.0],
        'Close': [102.0, 103.0, 104.0, 105.0, 106.0],
        'Adj Close': [102.0, 103.0, 104.0, 105.0, 106.0],
        'Volume': [1000, -1100, 1200, 1300, 1400]  # Negative volume
    }, index=dates)

    errors = await validator.validate_data(data)
    assert len(errors) > 0
    assert any('Price inconsistency' in e['error'] for e in errors)
    assert any('Invalid volume' in e['error'] for e in errors)
```

### 4. Testing the Implementation

1. Run the test suite:

   ```bash
   pytest cream_api/tests/stock_data/test_validator.py -v
   ```

2. Test with real data:

   ```python
   import asyncio
   from cream_api.db import get_session
   from cream_api.stock_data.retriever import StockDataRetriever

   async def main():
       async with get_session() as session:
           retriever = StockDataRetriever(session)
           try:
               await retriever.get_historical_data('AAPL', '2023-01-01')
               print("Data retrieved and validated successfully")
           except Exception as e:
               print(f"Error: {str(e)}")

   asyncio.run(main())
   ```

### 5. Next Steps

After implementing and testing data validation, proceed to Step 4: Error Handling and Rate Limiting Implementation.
