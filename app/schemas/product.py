from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str
    category: str
    tags: str

class ProductCreate(ProductBase):
    pass


class ProductSchema(ProductBase):
    id: int

    class Config:
        from_attributes = True