from flask import Flask
from flask_cors import CORS
from sqlalchemy import event
from app.core.config import settings
from app.db.session import SessionLocal
from app.extensions import db
from app.embeddings import faiss_service  # Import the singleton instance
import json
from app.schemas.product import ProductSchema  # Import your ProductSchema


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ProductSchema):
            return obj.model_dump()  # Convert ProductSchema to a dictionary
        return super().default(obj)


def create_app():
    app = Flask(__name__)
    CORS(app)
    # Use the custom encoder in your Flask app
    app.json_encoder = CustomJSONEncoder

    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["FLASK_RUN_OPTIONS"] = {"threaded": False}

    # Initialize extensions
    db.init_app(app)

    # Import these after db initialization to avoid circular imports
    from app.models.product import Product  # noqa
    from app.api.namespaces import api
    from app.mock_data import create_mock_data

    with app.app_context():
        # Create database tables
        db.create_all()

        print("before mock")
        create_mock_data(db.session)
        print("after mock")

        # Initialize FAISS service
        try:
            faiss_service.initialize_index()
        except ValueError as e:
            print(str(e))

    # Initialize Flask-RestX API
    api.init_app(app)

    app.session_local = SessionLocal

    @app.teardown_appcontext
    def close_session(exception=None):
        db.session.remove()

    @event.listens_for(db.session, "after_attach")
    def on_attach(session, instance):
        if not session.app.debug:
            session.configure(expire_on_commit=False)

    @event.listens_for(db.session, "after_rollback")
    def on_rollback(session):
        session.rollback()

    return app
