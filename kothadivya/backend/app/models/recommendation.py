from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.database import Base   # ✅ THIS WAS MISSING

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, nullable=False)
    message = Column(String)          # keep only if DB has column
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
