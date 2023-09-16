from fastapi import APIRouter, Query
from api.database import SessionLocal
from api.models import Product, Price

router = APIRouter()

# Define the route to get prices for a particular service
@router.get("/prices/{service_code}")
async def get_prices_for_service(service_code: str, skip: int = Query(0, ge=0), limit: int = Query(100, le=100000)):
    # Query the Product table to retrieve prices for the specified service
    with SessionLocal() as db:
        query = db.query(Product.id.label("product_id"), Product.sku.label("sku"), Product.location.label("location"), Product.region_code.label("region_code"), Price.pricePerUnit.label("price"), Price.unit.label("unit"))\
                .join(Price, Price.product_id == Product.id)\
                .filter(Product.service_code == service_code)\
                .offset(skip)\
                .limit(limit)\
                .all()

        # Convert the query results to a list of dictionaries
        prices = [{"product_id":row.product_id, "sku":row.sku, "location": row.location, "region_code": row.region_code, "price": row.price, "unit": row.unit} for row in query]

    return prices