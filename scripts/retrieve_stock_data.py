#!/usr/bin/env python3
"""Command-line interface for retrieving stock data from Yahoo Finance."""

import asyncio
import json
import os
from datetime import datetime

import click
from stargazer_utils.logging import get_logger_for

from cream_api.stock_data.config import get_stock_data_config
from cream_api.stock_data.retriever import StockDataRetriever

logger = get_logger_for(__name__)


def generate_ai_report(symbol: str, end_date: str | None, success: bool, error_message: str | None) -> None:
    """Generate AI report for stock data retrieval."""
    # Get project root and AI output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    ai_output_dir = os.path.join(project_root, "ai", "outputs", "stock_data_operations")

    # Ensure output directory exists
    os.makedirs(ai_output_dir, exist_ok=True)

    # Generate report
    timestamp = datetime.now().isoformat()
    report = {
        "metadata": {
            "title": "Stock Data Retrieval Results",
            "description": "Results from stock data retrieval operation",
            "version": "1.0.0",
            "last_updated": timestamp,
            "source": "scripts/retrieve_stock_data.py",
            "cross_references": ["cream_api/stock_data/", "pyproject.toml"],
        },
        "stock_data_retrieval": {
            "success": success,
            "symbol": symbol,
            "end_date": end_date,
            "timestamp": timestamp,
            "error_message": error_message,
        },
        "environment": {
            "python_version": "3.x",
            "working_directory": project_root,
            "project_root": project_root,
        },
    }

    # Save report
    report_file = os.path.join(ai_output_dir, "stock-data-retrieval-results.json")
    with open(report_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    click.echo(f"📄 AI report saved to: {report_file}")


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

        # Generate AI report for success
        generate_ai_report(symbol, end_date, True, None)

    except Exception as e:
        error_message = str(e)
        logger.error("Failed to retrieve stock data: %s", error_message)

        # Generate AI report for failure
        generate_ai_report(symbol, end_date, False, error_message)

        raise click.ClickException(error_message) from e


if __name__ == "__main__":
    retrieve_stock_data()
