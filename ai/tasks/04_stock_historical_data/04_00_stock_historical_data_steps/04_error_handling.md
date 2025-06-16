# Step 4: Error Handling Implementation

## Overview

In this step, we'll implement robust error handling to ensure reliable data retrieval and proper error reporting.

## Tasks

### 1. Create Custom Exceptions

In `cream_api/stock_data/exceptions.py`:

```python
class StockDataError(Exception):
    """Base exception for stock data related errors."""
    pass

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
```

### 2. Update Data Retriever

In `cream_api/stock_data/retriever.py`, update the class:

```python
from .exceptions import APIError, ValidationError

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
                raise ValidationError(symbol, errors)

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

        except (APIError, ValidationError) as e:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            raise APIError(symbol, f"Unexpected error: {str(e)}")
```

### 3. Create Tests

In `cream_api/tests/stock_data/test_error_handling.py`:

```python
import pytest
from datetime import datetime, timedelta
from cream_api.stock_data.exceptions import APIError, ValidationError
from cream_api.stock_data.retriever import StockDataRetriever

@pytest.mark.asyncio
async def test_retriever_error_handling(session):
    retriever = StockDataRetriever(session)

    # Test with invalid symbol
    with pytest.raises(APIError) as exc_info:
        await retriever.get_historical_data('INVALID_SYMBOL', '2023-01-01')
    assert 'INVALID_SYMBOL' in str(exc_info.value)

    # Test with invalid date range
    with pytest.raises(ValidationError) as exc_info:
        await retriever.get_historical_data('AAPL', '2023-01-01', '2022-12-31')
    assert 'AAPL' in str(exc_info.value)
```

### 4. Testing the Implementation

1. Run the test suite:

   ```bash
   pytest cream_api/tests/stock_data/test_error_handling.py -v
   ```

2. Test with real data and error scenarios:

   ```python
   import asyncio
   from cream_api.db import get_session
   from cream_api.stock_data.retriever import StockDataRetriever
   from cream_api.stock_data.exceptions import APIError, ValidationError

   async def main():
       async with get_session() as session:
           retriever = StockDataRetriever(session)
           try:
               await retriever.get_historical_data('AAPL', '2023-01-01')
               print("Data retrieved successfully")
           except APIError as e:
               print(f"API error: {str(e)}")
           except ValidationError as e:
               print(f"Validation error: {str(e)}")

   asyncio.run(main())
   ```

### 5. Next Steps

After implementing and testing error handling, proceed to Step 5: Rate Limiting Implementation.
