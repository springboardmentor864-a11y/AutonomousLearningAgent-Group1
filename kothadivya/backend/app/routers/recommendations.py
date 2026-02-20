from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.recommendation import Recommendation

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)

@router.get("/")
def get_recommendations(
    unread: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    )

    if unread:
        query = query.filter(Recommendation.is_read == False)

    return query.all()
