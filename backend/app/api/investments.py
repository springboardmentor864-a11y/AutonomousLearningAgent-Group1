from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.investment import Investment
from app.schemas.investment import InvestmentCreate, InvestmentResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.services.yahoo_service import get_stock_summary  # ✅ Yahoo Finance

router = APIRouter(
    prefix="/investments",
    tags=["Investments"]
)

@router.post("/", response_model=InvestmentResponse)
def create_investment(
    investment_data: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ✅ Fetch stock prices
    stock = get_stock_summary(investment_data.symbol.upper())

    if not stock:
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    # ✅ Create investment
    investment = Investment(
        user_id=current_user.id,
        symbol=investment_data.symbol.upper(),
        quantity=investment_data.quantity,
        buy_price=investment_data.buy_price,

        # 🔥 Values you asked about
        current_value=stock["current_value"],
        last_price=stock["last_price"]
    )

    db.add(investment)
    db.commit()
    db.refresh(investment)

    return investment
