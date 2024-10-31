from flask import Blueprint
from .namespaces import api
from .routes.products import products_ns

api_bp = Blueprint("api", __name__)
api.add_namespace(products_ns)
