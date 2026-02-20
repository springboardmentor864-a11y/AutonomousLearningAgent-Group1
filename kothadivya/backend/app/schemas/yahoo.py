from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class StockResponse(BaseModel):
    symbol: str
    company_name: str
    currency: str

    current_value: Decimal
    last_price: Optional[Decimal]

    day_high: Optional[float]
    day_low: Optional[float]
    market_cap: Optional[int]

    class Config:
        from_attributes = True
