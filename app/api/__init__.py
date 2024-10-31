<<<<<<< HEAD
=======
from flask import Blueprint
from .namespaces import api
from .routes.products import products_ns

api_bp = Blueprint("api", __name__)
api.add_namespace(products_ns)
>>>>>>> db4d8f8... fix: Migrate from FastAPI to FlaskAPI due to dependency issues
