# app/services/product_service.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
import numpy as np
from app.embeddings import vector_store


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_similar_products(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    tags = product.tags.split(',') if product.tags else []
    filters = [Product.tags.like(f"%{tag.strip()}%") for tag in tags]
    similar_products = db.query(Product).filter(Product.id != product_id).filter(or_(*filters)).all()
    return similar_products


async def get_similar_products_embeddings(db: Session, product_id: int, top_k: int = 3):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None  # Handle product not found

    if vector_store:
        similar_docs = vector_store.similarity_search_with_score(
            product.description, k=top_k
        )
        similar_product_ids = [doc.metadata["product_id"] for doc, _ in similar_docs]
        return similar_product_ids
    else:
        return []  # Handle case where vector_store is not initialized
