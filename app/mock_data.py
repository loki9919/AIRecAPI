from sqlalchemy.orm import Session
from app.models.product import Product
from app.embeddings import initialize_vector_store
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.docstore.document import Document

def create_mock_data(db: Session):  # Removed async
    """Create mock data and initialize the vector store."""
    # Check if we already have products
    existing_products = db.query(Product).all()
    if existing_products:
        return

    # Sample product data
    products_data = [
        {
            "name": "Wireless Noise-Cancelling Headphones",
            "description": "Experience immersive audio with these premium noise-cancelling headphones. Crystal-clear sound, comfortable over-ear design, and long battery life.",
            "category": "Electronics",
            "tags": "headphones,audio,noise-cancelling"
        },
        {
            "name": "The Art of War",
            "description": "A timeless classic on military strategy. Explore ancient wisdom and learn the principles of warfare.",
            "category": "Books",
            "tags": "strategy,military,classic"
        },
        {
            "name": "Elegant Evening Dress",
            "description": "Make a statement in this stunning evening gown. Featuring a flowing silhouette and intricate beading.",
            "category": "Clothing",
            "tags": "dress,fashion,eveningwear"
        },
        {
            "name": "High-Powered Electric Drill",
            "description": "Tackle any DIY project with this powerful electric drill. Variable speed control and durable construction.",
            "category": "Tools",
            "tags": "drill,power tools,hardware"
        },
        {
            "name": "Gourmet Coffee Beans",
            "description": "Indulge in the rich aroma and flavor of these premium coffee beans. Ethically sourced and expertly roasted.",
            "category": "Food & Drink",
            "tags": "coffee,gourmet,beans"
        }
    ]

    # Create products in database
    db_products = []
    for product_data in products_data:
        db_product = Product(**product_data)
        db.add(db_product)
        db_products.append(db_product)
    db.commit()

    # Prepare documents for vector store
    docs = []
    for product in db_products:
        # Create a document combining product info
        content = f"Name: {product.name}\nDescription: {product.description}\nCategory: {product.category}\nTags: {product.tags}"
        doc = Document(
            page_content=content,
            metadata={"product_id": product.id}
        )
        docs.append(doc)

    # Initialize vector store with documents
    initialize_vector_store(docs)
    return db_products
