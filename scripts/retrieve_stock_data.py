#!/usr/bin/env python3
"""Command-line interface for retrieving stock data from Yahoo Finance."""

import asyncio

import click
from stargazer_utils.logging import get_logger_for

from cream_api.stock_data.config import get_stock_data_config
from cream_api.stock_data.retriever import StockDataRetriever

logger = get_logger_for(__name__)


@click.command()
@click.argument("symbol", type=str)
@click.option("--end-date", type=str, help="End date in YYYY-MM-DD format (defaults to today)", default=None)
def retrieve_stock_data(symbol: str, end_date: str | None) -> None:
    """Retrieve historical stock data for a given symbol from Yahoo Finance.

    SYMBOL: The stock symbol to fetch data for (e.g., AAPL, MSFT)
    """
    try:
        config = get_stock_data_config()
        retriever = StockDataRetriever(config=config)
        asyncio.run(retriever.get_historical_data(symbol, end_date))
        click.echo(f"Successfully retrieved data for {symbol}")
    except Exception as e:
        logger.error("Failed to retrieve stock data: %s", str(e))
        raise click.ClickException(str(e)) from e


if __name__ == "__main__":
    retrieve_stock_data()
