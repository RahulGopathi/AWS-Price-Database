from fastapi import APIRouter, Query
from api.database import SessionLocal
from api.models import ProductFamily

router = APIRouter()


# Route to get all product families
@router.get("/product-families/")
async def get_product_families(skip: int = Query(0, description="Skip N product families", ge=0),
                               limit: int = Query(100, description="Limit the number of results", le=1000)):
    # Query the database for product families
    with SessionLocal() as db:
        product_families = db.query(ProductFamily).offset(skip).limit(limit).all()
    return product_families
