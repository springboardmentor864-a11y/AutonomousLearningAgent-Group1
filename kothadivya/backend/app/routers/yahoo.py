from fastapi import APIRouter, HTTPException
from app.services.yahoo_service import get_stock_summary
from app.schemas.yahoo import StockResponse   # ✅ IMPORTANT

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/stock/{symbol}", response_model=StockResponse)
def fetch_stock(symbol: str):
    stock = get_stock_summary(symbol.upper())

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    return stock
