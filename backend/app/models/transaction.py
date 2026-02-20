from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    transaction_type = Column(String, nullable=False)

    amount = Column(Numeric, nullable=False)
    description = Column(String(255))

    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="transactions")
