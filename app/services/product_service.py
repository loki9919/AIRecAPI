from typing import List
from app.schemas.product import ProductSchema
from app.embeddings import faiss_service
from app.extensions import db  # Import db from extensions.py
from app.models.product import Product


def get_similar_products(query: str, top_k: int = 5) -> List[ProductSchema]:
    """Get similar products using FAISS."""
    results = faiss_service.search(query, top_k)
    similar_products = []
    for result in results:
        # Use db.session to create a new session
        with db.session() as session:
            product = (
                session.query(Product)
                .filter(Product.id == result["product_id"])
                .first()
            )
            if product:
                similar_products.append(
                    ProductSchema(
                        id=product.id,
                        name=product.name,
                        description=product.description,
                        category=product.category,
                        tags=product.tags,
                    )
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