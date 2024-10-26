from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.security import get_api_key
from app.db.session import get_db
from app.services import product_service

router = APIRouter()

@router.get("/similar-products/{product_id}")
async def get_similar_products(
    product_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    similar_products = product_service.get_similar_products(db, product_id)
    if not similar_products:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"similar_product_ids": [p.id for p in similar_products]}

@router.get("/similar-products-ai/{product_id}")
async def get_similar_products_ai(
    product_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    similar_product_ids = product_service.get_similar_products_embeddings(db, product_id)
    return {"similar_product_ids": similar_product_ids}


@router.api_route("/api/v1/{path:path}", methods=["*"])
async def api_key_catch_all(request: Request, api_key: str = Depends(get_api_key)):
    raise HTTPException(status_code=404, detail="Not Found")
