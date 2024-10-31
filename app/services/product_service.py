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