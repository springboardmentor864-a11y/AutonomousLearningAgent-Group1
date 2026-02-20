# backend/app/models/investment.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from app.models.user import User  # assuming you have a User model

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_type = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    units = Column(Float, nullable=False)
    avg_buy_price = Column(Float, nullable=False)
    
    # Optional fields for tracking current value / PnL
   
    last_price_at = Column(DateTime)          # 🔴 REQUIRED
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = relationship("User", back_populates="investments")
