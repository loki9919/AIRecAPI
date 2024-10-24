from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, APIKeyQuery
from sqlalchemy import create_engine, Column, Integer, String, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch API keys and database URL from .env
API_KEYS = os.getenv("API_KEYS").split(",")
DATABASE_URL = os.getenv("DATABASE_URL")

print("Loaded API Keys:", API_KEYS)

# Initialize database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Product schema
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    tags = Column(String)

# Create tables if not already present
Base.metadata.create_all(bind=engine)

# Authentication setup
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api-key", auto_error=False)

app = FastAPI()

def get_api_key(api_key_header: str = Security(api_key_header),
                api_key_query: str = Security(api_key_query)) -> str:
    if api_key_header in API_KEYS:
        return api_key_header
    if api_key_query in API_KEYS:
        return api_key_query
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Secure Product API!"}

@app.on_event("startup")
def create_sample_data():
    db = SessionLocal()
    if not db.query(Product).first():  # Check if the database is empty
        sample_products = [
            Product(name="Product A", description="Description of Product A", category="Category 1", tags="tag1,tag2"),
            Product(name="Product B", description="Description of Product B", category="Category 1", tags="tag1,tag3"),
            Product(name="Product C", description="Description of Product C", category="Category 2", tags="tag2,tag4")
        ]
        db.bulk_save_objects(sample_products)
        db.commit()
    db.close()

@app.get("/similar-products/{product_id}")
def get_similar_products(product_id: int, db: Session = Depends(get_db), 
                         api_key: str = Depends(get_api_key)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    tags = product.tags.split(',')
    filters = [Product.tags.like(f"%{tag.strip()}%") for tag in tags]  # Strip whitespace
    similar_products = db.query(Product).filter(Product.id != product_id).filter(or_(*filters)).all()

    return {"similar_product_ids": [p.id for p in similar_products]}
