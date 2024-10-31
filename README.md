markdown
# 🚀 AI-Powered Product Recommendation API

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23000.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence%20Transformers-orange?style=flat&logo=HuggingFace)](https://www.sbert.net/)
[![FAISS](https://img.shields.io/badge/FAISS-blueviolet?style=flat&logo=facebook)](https://github.com/facebookresearch/faiss)


This project provides a robust and scalable product recommendation API powered by semantic search.  It allows you to build intelligent product discovery features into your applications, enabling users to find relevant products using natural language queries. ✨


## ✨ Key Features

* **Semantic Search:**  Understands user intent using Sentence Transformers and FAISS for accurate recommendations.
* **Scalable API:**  Built with Flask and Flask-RESTX for a structured and efficient API design.
* **Database Integration:**  Uses SQLAlchemy for flexible database management (SQLite for development, easily switchable to PostgreSQL for production).
* **Easy Integration:**  Simple JSON request/response format for seamless integration with your applications.


## 🚀 How It Works

1. **User Input:**  A user provides a natural language query (e.g., "comfortable running shoes for men").
2. **Semantic Embedding:** The API converts the query and product descriptions into numerical vectors using Sentence Transformers, capturing the semantic meaning.
3. **Similarity Search (FAISS):**  The API efficiently searches for the most similar product vectors using the FAISS library.
4. **Product Retrieval:** The API retrieves the corresponding product details from the database.
5. **Recommendation Output:** The API returns a JSON response containing the top recommended products, including titles, descriptions, prices, and more.


## 🛠 Tech Stack

* **Python 3:** Primary programming language.
* **Flask/Flask-RESTX:**  API framework and organization.
* **SQLAlchemy:**  Database ORM.
* **Sentence Transformers:** Semantic embeddings.
* **FAISS:** Similarity search.
* **SQLite (Development):** Database for development.
* **PostgreSQL (Production - Recommended):** Database for production.



## 📂 Project Structure

* **`app/api/routes/products.py`:** API endpoints for recommendations.
* **`app/services/product_service.py`:** Product data business logic.
* **`app/models/product.py`:** SQLAlchemy product model.
* **`app/embeddings/faiss_service.py`:** FAISS index management.
* **`app/core/config.py`:** API configuration.
* **`requirements.txt`:** Project dependencies.


## 🐳 Installation and Setup

1. Clone the repository:  `git clone https://github.com/your-username/your-repo.git`
2. Create a virtual environment:  `python3 -m venv .venv`
3. Activate the virtual environment:  `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
4. Install dependencies:  `pip install -r requirements.txt`
5. Set up the database (refer to the project documentation for database-specific instructions).
6. Run the API: `flask run` (for development) or use a production-ready WSGI server like Gunicorn.


## 🧪 Usage (Example with Curl)

bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"query": "comfortable running shoes for men", "top_k": 3}' \
     http://your-api-endpoint/products



## 🤝 Contributing

Contributions are welcome!  Please open an issue or submit a pull request.


## 📄 License

[MIT License](LICENSE)
