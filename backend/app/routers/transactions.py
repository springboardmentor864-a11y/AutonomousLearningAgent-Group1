from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# ✅ CREATE TRANSACTION
@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Debug (optional)
    print("Incoming transaction:", transaction)

    new_txn = Transaction(
        user_id=current_user.id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
    )

    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)

    return new_txn


# ✅ GET CURRENT USER TRANSACTIONS
@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )


# ✅ GET TRANSACTIONS BY USER ID
@router.get("/user/{user_id}", response_model=List[TransactionResponse])
def get_transactions_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .all()
    )
