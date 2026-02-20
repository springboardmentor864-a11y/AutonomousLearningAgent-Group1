from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ================================
# PostgreSQL Database URL
# ================================
DATABASE_URL = "postgresql://postgres:root@localhost:5432/wealth_management"

# ================================
# Engine
# ================================
engine = create_engine(DATABASE_URL)

# ================================
# Session
# ================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ================================
# Base (SINGLE SOURCE OF TRUTH)
# ================================
Base = declarative_base()

# ================================
# Dependency (FastAPI)
# ================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
