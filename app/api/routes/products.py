from flask_restx import Namespace, Resource
from flask import request
from app.services.product_service import get_similar_products
from app.schemas.product import ProductSchema
import json  # Import the json module

products_ns = Namespace("products", description="Product operations")


@products_ns.route("/")
class ProductList(Resource):
    def post(self):
        try:
            # Get query parameters
            query = request.json.get("query")
            top_k = request.json.get("top_k", 5)

            if not query:
                products_ns.abort(400, "Query parameter is required")

            similar_products = get_similar_products(query, top_k)
            # Serialize using the custom encoder
            return json.dumps(similar_products, cls=CustomJSONEncoder)

        except RuntimeError as e:
            products_ns.abort(503, f"Search service unavailable: {str(e)}")
        except ValueError as e:
            products_ns.abort(400, str(e))
        except Exception as e:
            # Capture the error and send it to the client
            print(f"Internal server error: {str(e)}")
            return {
                "error": str(e)
            }, 500  # Return the error message and a 500 status code


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ProductSchema):
            return obj.dict()
        return super().default(obj)
