"""FastAPI endpoints for stock data retrieval."""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from cream_api.stock_data.retriever import StockDataRetriever

router = APIRouter(prefix="/stock-data", tags=["stock-data"])


class StockDataRequest(BaseModel):
    """Request model for stock data retrieval."""

    symbol: str
    end_date: str | None = None


async def _retrieve_historical_data(symbol: str, end_date: str | None) -> None:
    """Background task to retrieve historical stock data.

    Args:
        symbol: Stock symbol to retrieve data for
        end_date: Optional end date in YYYY-MM-DD format
    """
    retriever = StockDataRetriever()
    await retriever.get_historical_data(
        symbol=symbol,
        end_date=end_date,
    )


@router.post("/historical")
async def get_historical_data(
    request: StockDataRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """Schedule historical stock data retrieval for a given symbol.

    Args:
        request: StockDataRequest containing symbol and optional end_date
        background_tasks: FastAPI background tasks manager

    Returns:
        dict: Response indicating the task has been scheduled

    Raises:
        HTTPException: If there's an error scheduling the task
    """
    try:
        background_tasks.add_task(
            _retrieve_historical_data,
            symbol=request.symbol,
            end_date=request.end_date,
        )
        return {
            "status": "scheduled",
            "message": f"Historical data retrieval for {request.symbol} has been scheduled",
            "symbol": request.symbol,
            "end_date": request.end_date,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
