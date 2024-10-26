from sqlalchemy.orm import Session
from app.models.product import Product
from app.embeddings import generate_embedding, embedding_model, vector_store
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter


def create_mock_data(db: Session):
    existing_products = db.query(Product).all()
    if existing_products:
        return

    products_data = [
        {"name": "Wireless Noise-Cancelling Headphones", "description": "Experience immersive audio with these premium noise-cancelling headphones. Crystal-clear sound, comfortable over-ear design, and long battery life.", "category": "Electronics", "tags": "headphones,audio,noise-cancelling"},
        {"name": "The Art of War", "description": "A timeless classic on military strategy. Explore ancient wisdom and learn the principles of warfare.", "category": "Books", "tags": "strategy,military,classic"},
        {"name": "Elegant Evening Dress", "description": "Make a statement in this stunning evening gown. Featuring a flowing silhouette and intricate beading.", "category": "Clothing", "tags": "dress,fashion,eveningwear"},
        {"name": "High-Powered Electric Drill", "description": "Tackle any DIY project with this powerful electric drill. Variable speed control and durable construction.", "category": "Tools", "tags": "drill,power tools,hardware"},
        {"name": "Gourmet Coffee Beans", "description": "Indulge in the rich aroma and flavor of these premium coffee beans. Ethically sourced and expertly roasted.", "category": "Food & Drink", "tags": "coffee,gourmet,beans"}
    ]

    db_products = []
    for product_data in products_data:
        db_product = Product(**product_data)
        db.add(db_product)
        db_products.append(db_product)
    db.commit()

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
        ("#####", "Header 5"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    docs = []
    for product in db_products:
        md_header_splits = markdown_splitter.split_text(product.description)
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=512, chunk_overlap=256)
        splits = text_splitter.split_documents(md_header_splits)
        for split in splits:
            split.metadata["product_id"] = product.id
        docs.extend(splits)


    global vector_store  # Use the global vector_store
    vector_store = Chroma.from_documents(docs, embedding_model)