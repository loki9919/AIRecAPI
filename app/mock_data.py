# app/mock_data.py
from sqlalchemy.orm import Session
from app.models.product import Product
from app.extensions import db


def create_mock_data(dbsession: Session):
    """Create mock data and initialize the vector store."""
    # Check if we already have products
    existing_products = dbsession.query(Product).all()
    if existing_products:
        return

    # Sample product data
    products_data = [
        {
            "name": "Wireless Noise-Cancelling Headphones",
            "description": "Experience immersive audio with these premium noise-cancelling headphones. Crystal-clear sound, comfortable over-ear design, and long battery life.",
            "category": "Electronics",
            "tags": "headphones,audio,noise-cancelling",
        },
        {
            "name": "The Art of War",
            "description": "A timeless classic on military strategy. Explore ancient wisdom and learn the principles of warfare.",
            "category": "Books",
            "tags": "strategy,military,classic",
        },
    ]

    # Create products in database
    db_products = []
    for product_data in products_data:
        db_product = Product(**product_data)
        dbsession.add(db_product)
        db_products.append(db_product)
    dbsession.commit()

    return db_products