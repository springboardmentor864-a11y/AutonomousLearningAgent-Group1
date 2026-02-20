from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.investment import Investment

router = APIRouter(prefix="/investments", tags=["Investments"])

@router.get("/user/{user_id}")
def get_user_investments(user_id: int, db: Session = Depends(get_db)):
    investments = (
        db.query(Investment)
        .filter(Investment.user_id == user_id)
        .all()
    )
    return investments
