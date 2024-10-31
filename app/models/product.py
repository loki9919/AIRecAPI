# app/models/product.py
from sqlalchemy import Column, Integer, String
from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    tags = Column(String)