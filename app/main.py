from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.api.endpoints import products
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.security import get_api_key
from app.models.product import Product
from app.mock_data import create_mock_data

app = FastAPI(title=settings.PROJECT_NAME)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(products.router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():  # Removed async
    """Initialize database and vector store on startup."""
    db = SessionLocal()
    try:
        # Create mock data and initialize vector store
        create_mock_data(db)  # Removed await
    finally:
        db.close()

@app.get("/")
async def read_root():
    return {"message": "Root endpoint (unprotected)"}