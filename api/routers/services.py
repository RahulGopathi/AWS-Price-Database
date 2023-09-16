from fastapi import APIRouter, Query
from api.database import SessionLocal
from api.models import ProductFamily, Product

router = APIRouter()

# Route to get all services under a product family
@router.get("/services/{product_family_name}")
async def get_services(product_family_name: str, skip: int = Query(0, ge=0), limit: int = Query(100, le=100000)):
    # Query the database for services under the specified product family
    with SessionLocal() as db:
        services = db.query(Product).filter(Product.product_family_id == ProductFamily.id,
                                             ProductFamily.name == product_family_name).offset(skip).limit(limit).all()
    return services

# Define the route to get all services available in a region
@router.get("/services/")
async def get_services_in_region(region: str = Query(..., description="Region code")):
    # Query the Product table to retrieve services available in the specified region
    with SessionLocal() as db:
        query = db.query(Product.service_code)\
                        .filter(Product.region_code == region)\
                        .distinct()\
                        .all()

        # Convert the query results to a list of service codes
        service_codes = [service[0] for service in query]

    return service_codes
