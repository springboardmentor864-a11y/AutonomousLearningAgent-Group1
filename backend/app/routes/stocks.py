from fastapi import APIRouter
from app.services.yahoo_finance import get_stock_price

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("/{symbol}")
def stock_data(symbol: str):
    return get_stock_price(symbol)
