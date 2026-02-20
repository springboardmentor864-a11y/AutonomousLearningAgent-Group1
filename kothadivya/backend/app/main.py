from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models.user import User
from app.models.investment import Investment
from app.models.transaction import Transaction

from app.routers import auth, goals, investments, transactions, recommendations
from .routes.reports import router as reports_router
from app.routers import yahoo

from app.routes.stocks import router as stocks_router
# ================================
# Create DB tables
# ================================
User.metadata.create_all(bind=engine)
Investment.metadata.create_all(bind=engine)
Transaction.metadata.create_all(bind=engine)

# ================================
# FastAPI app
# ================================
app = FastAPI(title="Wealth Management Backend")

# ================================
# CORS configuration (allow all origins)
# ================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[  
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# Include routers
# ================================
app.include_router(auth.router)
app.include_router(goals.router)
app.include_router(investments.router)
app.include_router(transactions.router)
app.include_router(recommendations.router)
app.include_router(reports_router)
app.include_router(yahoo.router)
app.include_router(stocks_router)


 
# ================================
# Root endpoint
# ================================
@app.get("/")
def root():
    return {"status": "working 🚀"}
