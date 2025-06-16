# Step 2: Basic Data Retrieval Implementation

## Overview

In this step, we'll implement the basic functionality to retrieve stock data from Yahoo Finance using async operations and the requests library.

## Tasks

### 1. Create Basic Data Retriever

In `cream_api/stock_data/retriever.py`:

```python
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import aiohttp
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from .models import StockData

class StockDataRetriever:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    async def _fetch_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch stock data from Yahoo Finance API.

        Args:
            symbol (str): Stock symbol
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format

        Returns:
            Dict[str, Any]: Raw API response data
        """
        # Convert dates to timestamps
        start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

        # Construct URL with parameters
        url = f"{self.base_url}/{symbol}"
        params = {
            'period1': start_timestamp,
            'period2': end_timestamp,
            'interval': '1d',
            'includePrePost': 'false',
            'events': 'div,split'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                return await response.json()

    def _process_response(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process raw API response into a DataFrame.

        Args:
            data (Dict[str, Any]): Raw API response

        Returns:
            pd.DataFrame: Processed stock data
        """
        try:
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]

            df = pd.DataFrame({
                'Open': quotes['open'],
                'High': quotes['high'],
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            }, index=pd.to_datetime(timestamps, unit='s'))

            # Calculate adjusted close if splits/dividends exist
            if 'events' in result:
                if 'splits' in result['events']:
                    for split in result['events']['splits'].values():
                        split_date = pd.to_datetime(split['date'], unit='s')
                        split_ratio = split['numerator'] / split['denominator']
                        df.loc[df.index < split_date, 'Close'] *= split_ratio

            df['Adj Close'] = df['Close']
            return df

        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to process API response: {str(e)}")

    async def get_historical_data(self, symbol: str, start_date: str, end_date: Optional[str] = None) -> None:
        """
        Retrieve historical stock data and store it in the database.

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to today.
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        try:
            # Fetch data from API
            raw_data = await self._fetch_data(symbol, start_date, end_date)
            data = self._process_response(raw_data)

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

### 2. Create Basic Test

In `cream_api/tests/stock_data/test_retriever.py`:

```python
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from cream_api.stock_data.retriever import StockDataRetriever
from cream_api.stock_data.models import StockData

@pytest.mark.asyncio
async def test_get_historical_data(session: AsyncSession):
    retriever = StockDataRetriever(session)

    # Test with a known stock (Apple)
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    await retriever.get_historical_data('AAPL', start_date)

    # Verify data was stored
    result = await session.execute(
        "SELECT COUNT(*) FROM stock_data WHERE symbol = 'AAPL'"
    )
    count = result.scalar()
    assert count > 0

@pytest.mark.asyncio
async def test_invalid_symbol(session: AsyncSession):
    retriever = StockDataRetriever(session)

    # Test with an invalid symbol
    with pytest.raises(Exception) as exc_info:
        await retriever.get_historical_data('INVALID_SYMBOL', '2023-01-01')
    assert 'Error retrieving data' in str(exc_info.value)
```

### 3. Testing the Implementation

1. Run the test suite:

   ```bash
   pytest cream_api/tests/stock_data/test_retriever.py -v
   ```

2. Try retrieving data manually:

   ```python
   import asyncio
   from cream_api.db import get_session
   from cream_api.stock_data.retriever import StockDataRetriever

   async def main():
       async with get_session() as session:
           retriever = StockDataRetriever(session)
           try:
               await retriever.get_historical_data('AAPL', '2023-01-01')
               print("Data retrieved successfully")
           except Exception as e:
               print(f"Error: {str(e)}")

   asyncio.run(main())
   ```

### 4. Next Steps

After implementing and testing the basic retrieval functionality, proceed to Step 3: Data Validation Implementation.
