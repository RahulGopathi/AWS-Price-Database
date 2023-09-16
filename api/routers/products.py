from fastapi import APIRouter, Query
from api.database import SessionLocal
from api.models import Product

router = APIRouter()

# Route to get all products of a particular service
@router.get("/products/{service_code}")
async def get_products(service_code: str, skip: int = Query(0, ge=0), limit: int = Query(100, le=100000)):
    # Query the database for products of the specified service
    with SessionLocal() as db:
        products = db.query(Product).filter(Product.service_code == service_code).offset(skip).limit(limit).all()
    return products