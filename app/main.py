from fastapi import FastAPI
from app.api.endpoints import products
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title=settings.PROJECT_NAME)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(products.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Secure Product API!"}
