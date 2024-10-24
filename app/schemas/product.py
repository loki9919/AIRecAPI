from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    category: str
    tags: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True
