from fastapi import APIRouter, Query
from api.database import SessionLocal
from api.models import Product, Price
from api.utils.customHTTPException import CustomHTTPException

router = APIRouter()


# Route to get all products of a particular service
@router.get("/products/{service_code}")
async def get_products(service_code: str, skip: int = Query(0, ge=0), limit: int = Query(100, le=100000)):
    # Query the database for products of the specified service
    with SessionLocal() as db:
        products = db.query(Product).filter(Product.service_code == service_code).offset(skip).limit(limit).all()
    return products


# Route to get all products of a particular product attribute value
@router.get("/products/")
def get_products_by_attribute(
    attribute_name: str = Query(default="", description="Name of the product attribute"),
    attribute_value: str = Query(default="", description="Value of the product attribute"),
    include_prices: bool = Query(default=False, description="Include prices in the response"),
):
    if not attribute_name or not attribute_value:
        raise CustomHTTPException(status_code=400, detail="Missing query parameters")
    else:
        if include_prices:
            with SessionLocal() as db:

                product_prices = db.query(Product.id.label("product_id"), Product.product_family_id.label("product_family_id"),
                                          Product.service_code.label("service_code"), Product.sku.label("sku"),
                                          Product.location.label("location"), Product.region_code.label("region_code"),
                                          Price.pricePerUnit.label("price"), Price.unit.label("unit"),
                                          Price.description.label("description")).\
                                          join(Price, Product.id == Price.product_id).\
                                          filter(Product.product_attributes[attribute_name] == attribute_value).all()

                # Check if any products match the condition
                if not product_prices:
                    raise CustomHTTPException(status_code=404, detail="No products found with the specified condition")

                product_prices_result = [{"product_id": row.product_id, "product_family_id": row.product_family_id,
                                          "sku": row.sku, "location": row.location, "service_code": row.service_code,
                                          "region_code": row.region_code, "price": row.price, "unit": row.unit,
                                          "price_description": row.description} for row in product_prices]

            return product_prices_result
        else:
            with SessionLocal() as db:

                products = db.query(Product).filter(Product.product_attributes[attribute_name] == attribute_value).all()

                # Check if any products match the condition
                if not products:
                    raise CustomHTTPException(status_code=404, detail="No products found with the specified condition")

                product_list = [product.__dict__ for product in products]

            return product_list
