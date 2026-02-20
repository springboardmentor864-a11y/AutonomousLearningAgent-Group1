# backend/app/schemas/investment.py

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Schema for creating a new investment (request body)
class InvestmentCreate(BaseModel):
    asset_type: str
    symbol: str
    units: float
    avg_buy_price: float

# Schema for returning investment data (response)
class InvestmentResponse(BaseModel):
    id: int
    user_id: int
    asset_type: str
    symbol: str
    units: float
    avg_buy_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_price_at: Optional[datetime] = None
    unrealized_pnl: Optional[float] = None
    pnl_percent: Optional[float] = None

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode
