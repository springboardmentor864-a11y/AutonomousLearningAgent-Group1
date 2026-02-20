from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional

# =========================
# Enums (match User model)
# =========================
class RiskProfile(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"


class KYCStatus(str, Enum):
    unverified = "unverified"
    verified = "verified"
    rejected = "rejected"


# =========================
# Request Schemas
# =========================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    # risk_profile: RiskProfile = RiskProfile.moderate  # enable later if needed


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =========================
# Response Schemas
# =========================
class UserResponse(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    risk_profile: Optional[RiskProfile]
    kyc_status: KYCStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================
# Auth Schemas
# =========================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
