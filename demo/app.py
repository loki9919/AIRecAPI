import streamlit as st
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from PIL import Image


# Load the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load product data from CSV (replace 'products.csv' with your file)
try:
    df = pd.read_csv(
        "demo/data/products.csv"
    )  # Assumes columns: product_id, description, title, image_path
    # Check if 'image_path' column exists, if not, create a dummy one
    if "image_path" not in df.columns:
        df["image_path"] = ""  # Or a default image path if you have one
except FileNotFoundError:
    st.error("Please upload a 'products.csv' file.")
    st.stop()


# Generate embeddings for product descriptions (do this only once)
if "embeddings" not in st.session_state:
    descriptions = df["description"].tolist()
    st.session_state.embeddings = model.encode(descriptions)

    # Normalize embeddings
    st.session_state.embeddings = st.session_state.embeddings / np.linalg.norm(
        st.session_state.embeddings, axis=1, keepdims=True
    )

    # Initialize FAISS index
    index = faiss.IndexFlatIP(st.session_state.embeddings.shape[1])
    index.add(st.session_state.embeddings.astype(np.float32))
    st.session_state.index = index

    st.session_state.df = df  # Store the DataFrame in session state


def semantic_search(query, top_k=3):
    query_embedding = model.encode([query])
    query_embedding = query_embedding / np.linalg.norm(query_embedding)
    distances, indices = st.session_state.index.search(
        query_embedding.astype(np.float32), top_k
    )

    results = []
    for idx in indices[0]:
        row = st.session_state.df.iloc[idx]  # Access row directly from DataFrame
        results.append(row)  # Append the entire row
    return results


# Streamlit app
st.title("Product Recommendation Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What are you looking for?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Perform semantic search
    results = semantic_search(prompt)

    # Display results in the chat
    with st.chat_message("assistant"):
        for product in results:
            col1, col2 = st.columns([1, 2])
            with col1:
                try:
                    # Display image from local path
                    image = Image.open(product["image_path"])
                    st.image(image, use_column_width=True)

                except (
                    FileNotFoundError,
                    OSError,
                    AttributeError,
                ) as e:  # Handle various image errors
                    st.warning(
                        f"Image not found or couldn't be displayed for product ID {product['product_id']}. Error: {e}"
                    )

            with col2:
                st.markdown(f"**{product['title']}**")
                st.markdown(f"$ **{product['price']}**")
                st.markdown(product["description"])

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": ""}
    )  # Content is the image and text above
