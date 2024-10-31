import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.product import Product
from app.extensions import db
from typing import List, Dict, Optional


class FaissService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaissService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized") or not self._initialized:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.index: Optional[faiss.Index] = None
            self.product_ids: List[int] = []
            self.descriptions: List[str] = []
            self._initialized = True

    def __del__(self):
        if self.index is not None:
            try:
                # Release the FAISS index
                faiss.delete_index(self.index)
            except:
                pass
            self.index = None

    def initialize_index(self) -> None:
        try:
            all_products = db.session.query(Product).all()

            if not all_products:
                raise ValueError("No products found in database")

            self.descriptions = [product.description for product in all_products]
            self.product_ids = [product.id for product in all_products]

            description_embeddings = self.model.encode(self.descriptions)

            # Create a CPU index
            dimension = description_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)

            # Normalize the vectors before adding
            faiss.normalize_L2(description_embeddings)

            # Add the vectors to the index
            self.index = faiss.IndexIDMap(self.index)
            self.index.add_with_ids(
                description_embeddings.astype(np.float32),
                np.array(self.product_ids).astype(np.int64),
            )

            print(
                f"Successfully initialized FAISS index with {len(all_products)} products"
            )

        except Exception as e:
            print(f"Error initializing FAISS index: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if self.index is None:
            self.initialize_index()

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        try:
            # Encode and normalize the query
            query_embedding = self.model.encode([query])
            faiss.normalize_L2(query_embedding)

            # Perform the search
            distances, indices = self.index.search(
                query_embedding.astype(np.float32), min(top_k, len(self.product_ids))
            )

            # Build results
            recommended_products = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:  # Valid index
                    recommended_products.append(
                        {
                            "product_id": int(idx),
                            "description": self.descriptions[
                                self.product_ids.index(int(idx))
                            ],
                            "similarity_score": float(distances[0][i]),
                        }
                    )

            return recommended_products

        except Exception as e:
            print(f"Error during search: {str(e)}")
            raise

    def refresh_index(self) -> None:
        self.initialize_index()
