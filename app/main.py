from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.api.endpoints import products
from app.core.config import settings
from app.db.base import Base  # Make sure to import Base
from app.db.session import engine, SessionLocal
from app.core.security import get_api_key
from app.models.product import Product

app = FastAPI(title=settings.PROJECT_NAME)

Base.metadata.create_all(bind=engine)

app.include_router(products.router, prefix="/api/v1")


@app.get("/")  # Example unprotected endpoint
async def read_root():
    return {"message": "Root endpoint (unprotected)"}

def create_mock_data(db: Session):
    """Creates some mock product data."""

    existing_products = db.query(Product).all()
    if existing_products:
        return  # Don't create data if it already exists

    products_data = [
        {"name": "Product A", "description": "Awesome product", "category": "Electronics", "tags": "gadget,new"},
        {"name": "Product B", "description": "Another great product", "category": "Books", "tags": "fiction,new"},
        {"name": "Product C", "description": "Amazing product", "category": "Clothing", "tags": "fashion,sale"},
        {"name": "Product D", "description": "Excellent product", "category": "Tools", "tags": "hardware,discount"},

        # Add more product data as needed
    ]

    for product_data in products_data:
        db_product = Product(**product_data)
        db.add(db_product)

    db.commit()


@app.on_event("startup")
async def startup_event():
    """Create mock data on startup."""
    db = SessionLocal()
    try:
        create_mock_data(db)
    finally:
        db.close()