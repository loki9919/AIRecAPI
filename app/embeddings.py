from fastembed.embedding import DefaultEmbedding
from langchain.vectorstores import Chroma
from app.models.product import Product

embedding_model = DefaultEmbedding()
vector_store = None


async def generate_embedding(text):
    return embedding_model.embed(text)