# Stock Data Parser Technical Summary

## Overview
The `StockDataParser` class is responsible for extracting and processing stock market data from HTML content. It provides functionality to parse HTML strings or files, extract tabular data, and convert it into a structured pandas DataFrame.

## Key Components

### Required Constants
- `HISTORICAL_PRICES_CSS_SELECTOR = ".gridLayout > div:nth-child(2)"` - CSS selector for locating the historical prices table
- `REQUIRED_COLUMNS_COUNT` - Number of required columns in the data table

### Required Columns
The parser expects the following columns in the input data:
- Date
- Open
- High
- Low
- Close
- Adj Close
- Volume

### Column Mapping
The parser maps HTML headers to DataFrame columns using the following mapping:
```python
{
    "Date": "date",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume"
}
```

## Core Functionality

### 1. HTML Parsing
- `parse_html(html_content: str)` - Parses raw HTML string
- `parse_html_file(file_path: str)` - Parses HTML from a file
- Both methods return a dictionary with a "prices" key containing the extracted data

### 2. Data Processing
- `process_data(data: dict)` - Converts raw data into a pandas DataFrame
- Performs cleaning, validation, and normalization
- Returns a structured DataFrame with standardized column names

### 3. Data Validation
The parser implements several validation checks:
- Required columns presence
- Valid date ranges (between 1900-01-01 and current date)
- Valid price ranges (non-negative)
- Valid volume values (non-negative)
- Price relationship validation (high ≥ low, high ≥ open, high ≥ close, etc.)

### 4. Data Cleaning
The cleaning process includes:
- Converting dates to datetime format
- Removing commas from numeric values
- Converting numeric columns to appropriate types
- Removing duplicate entries
- Sorting by date
- Handling missing values:
  - Volume: filled with 0
  - Price columns: filled with mean values

## Error Handling
The parser uses a custom `StockRetrievalError` exception for error handling, covering:
- Invalid HTML content
- Missing data tables
- Invalid table structure
- Missing required columns
- Data validation failures
- File reading errors

## Dependencies
- BeautifulSoup4 - HTML parsing
- pandas - Data manipulation
- logging - Error logging

## Usage Example
```python
parser = StockDataParser()
html_content = "..."
data = parser.parse_html(html_content)
df = parser.process_data(data)
```
