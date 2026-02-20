from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: float
    category: str
    transaction_type: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True


class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str
    transaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True
