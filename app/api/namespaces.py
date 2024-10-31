# app/api/namespaces.py
from flask_restx import Api

api = Api(
    title="Your API Title",
    version="1.0",
    description="Your API Description",
    doc="/docs",
)
