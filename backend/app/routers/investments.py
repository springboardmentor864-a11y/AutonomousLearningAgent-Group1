from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from app.database import get_db
from app.models.investment import Investment
from app.schemas.investment import InvestmentCreate, InvestmentResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.services.yahoo_service import get_stock_summary

router = APIRouter(
    prefix="/investments",
    tags=["Investments"]
)

# ==============================
# Create investment
# POST /investments
# ==============================
@router.post("", response_model=InvestmentResponse)
def create_investment(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not investment.asset_type:
        raise HTTPException(status_code=400, detail="asset_type is required")
    if not investment.symbol:
        raise HTTPException(status_code=400, detail="symbol is required")

    new_investment = Investment(
        user_id=current_user.id,
        asset_type=investment.asset_type,
        symbol=investment.symbol,
        units=Decimal(investment.units),
        avg_buy_price=Decimal(investment.avg_buy_price),
        created_at=datetime.utcnow()
    )

    db.add(new_investment)
    db.commit()
    db.refresh(new_investment)

    return new_investment


# ==============================
# Get logged-in user's investments
# GET /investments/user
# ==============================
@router.get("/user")
def get_my_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Investment)
        .filter(Investment.user_id == current_user.id)
        .all()
    )


# ==============================
# Get investments by user ID
# GET /investments/user/{user_id}
# ==============================
@router.get("/user/{user_id}")
def get_investments_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Investment).filter(Investment.user_id == user_id).all()


# ==============================
# Get live stock price (NO DB UPDATE)
# GET /investments/price/{symbol}
# ==============================
@router.get("/price/{symbol}")
def get_latest_price(symbol: str):
    data = get_stock_summary(symbol)

    if not data or not data.get("current_price"):
        raise HTTPException(status_code=404, detail="Price not found")

    return {
        "symbol": data["symbol"],
        "current_price": data["current_price"]
    }


# ==============================
# Update investment price in DB
# PUT /investments/update-price/{investment_id}
# ==============================
@router.put("/update-price/{investment_id}")
def update_investment_price(
    investment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    investment = (
        db.query(Investment)
        .filter(
            Investment.id == investment_id,
            Investment.user_id == current_user.id
        )
        .first()
    )

    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    data = get_stock_summary(investment.symbol)

    if not data or not data.get("current_price"):
        raise HTTPException(status_code=404, detail="Live price not found")

    live_price = Decimal(str(data["current_price"]))

    # ✅ shift current → last
    investment.last_price = investment.current_price
    investment.current_price = live_price
    investment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(investment)

    return {
        "investment_id": investment.id,
        "symbol": investment.symbol,
        "last_price": investment.last_price,
        "current_price": investment.current_price
    }
