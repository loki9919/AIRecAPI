from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
import numpy as np
from app.embeddings import get_vector_store, generate_embedding

async def get_similar_products(db: Session, product_id: int) -> Optional[List[Product]]:
    """Get similar products based on tags."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    
    tags = product.tags.split(',') if product.tags else []
    if not tags:
        return []
        
    filters = [Product.tags.like(f"%{tag.strip()}%") for tag in tags]
    similar_products = (
        db.query(Product)
        .filter(Product.id != product_id)
        .filter(or_(*filters))
        .limit(5)
        .all()
    )
    return similar_products

async def get_similar_products_embeddings(
    db: Session, 
    product_id: int, 
    top_k: int = 3
) -> Optional[List[int]]:
    """Get similar products using embeddings."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    vector_store = get_vector_store()
    if not vector_store:
        return []

    similar_docs = vector_store.similarity_search(
        product.description, 
        k=top_k
    )
    similar_product_ids = [doc.metadata["product_id"] for doc in similar_docs]
    return similar_product_ids

async def get_similar_products_rag(
    db: Session, 
    product_id: int, 
    top_k: int = 3
) -> List[int]:
    """Get similar products using RAG (Retrieval-Augmented Generation)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return []

    vector_store = get_vector_store()
    if not vector_store:
        return []

    # Use both description and tags for better matching
    query = f"{product.description} {product.tags}"
    
    similar_docs = vector_store.similarity_search(
        query,
        k=top_k + 1  # Get one extra to filter out the original product
    )
    
    # Filter out the original product and get unique IDs
    similar_product_ids = []
    seen_ids = {product_id}
    
    for doc in similar_docs:
        doc_id = doc.metadata["product_id"]
        if doc_id not in seen_ids:
            similar_product_ids.append(doc_id)
            seen_ids.add(doc_id)
            if len(similar_product_ids) >= top_k:
                break
                
    return similar_product_ids