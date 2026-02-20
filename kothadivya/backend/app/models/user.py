from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base  # ✅ correct Base import


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 👤 Basic details
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # 📊 Profile info
    risk_profile = Column(String(20), default="moderate")
    kyc_status = Column(String(20), default="unverified")

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔁 Relationships
    investments = relationship(
        "Investment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
