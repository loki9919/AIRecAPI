from typing import Optional, List
from fastembed.embedding import DefaultEmbedding
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

# Global variables
embedding_model = DefaultEmbedding()
_vector_store: Optional[FAISS] = None

def get_vector_store() -> Optional[FAISS]:
    """Get the current vector store instance."""
    global _vector_store
    return _vector_store

def generate_embedding(text: str):
    """Generate embeddings for given text."""
    embeddings = embedding_model.embed(text)
    return next(embeddings)  # fastembed returns a generator

def initialize_vector_store(documents: List[Document]) -> None:
    """Initialize the vector store with documents."""
    global _vector_store
    
    if not documents:
        return
        
    # Create a new FAISS instance
    _vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embedding_model
    )

def clear_vector_store() -> None:
    """Clear the vector store data."""
    global _vector_store
    if _vector_store:
        _vector_store = None