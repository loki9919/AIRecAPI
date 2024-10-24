from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product

def get_similar_products(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    tags = product.tags.split(',')
    filters = [Product.tags.like(f"%{tag.strip()}%") for tag in tags]
    similar_products = db.query(Product).filter(Product.id != product_id).filter(or_(*filters)).all()
    return similar_products
