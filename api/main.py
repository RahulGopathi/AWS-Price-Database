from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create a FastAPI instance
app = FastAPI()

# Set up the database connection
DATABASE_URL = "mysql+mysqlconnector://aws:aws@10.22.0.140/aws_database"
engine = create_engine(DATABASE_URL)

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a SQLAlchemy Base model
Base = declarative_base()

# Define database models
class ProductFamily(Base):
    __tablename__ = "product_family"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    product_family_id = Column(Integer, index=True)
    sku = Column(String(255), index=True)
    service_code = Column(String(255), index=True)
    location = Column(String(255))
    region_code = Column(String(255))
    product_attributes = Column(JSON)

class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    pricePerUnit = Column(String(255))
    unit = Column(String(255))
    description = Column(String(255))

# Route to get all product families
@app.get("/product-families/")
async def get_product_families(skip: int = Query(0, description="Skip N product families", ge=0),
                               limit: int = Query(100, description="Limit the number of results", le=1000)):
    # Query the database for product families
    with SessionLocal() as db:
        product_families = db.query(ProductFamily).offset(skip).limit(limit).all()
    return product_families

# Route to get all services under a product family
@app.get("/services/{product_family_name}")
async def get_services(product_family_name: str, skip: int = Query(0, ge=0), limit: int = Query(100, le=100000)):
    # Query the database for services under the specified product family
    with SessionLocal() as db:
        services = db.query(Product).filter(Product.product_family_id == ProductFamily.id,
                                             ProductFamily.name == product_family_name).offset(skip).limit(limit).all()
    return services

# Route to get all products of a particular service
@app.get("/products/{service_code}")
async def get_products(service_code: str, skip: int = Query(0, ge=0), limit: int = Query(100, le=100000)):
    # Query the database for products of the specified service
    with SessionLocal() as db:
        products = db.query(Product).filter(Product.service_code == service_code).offset(skip).limit(limit).all()
    return products

# Define the route to get prices for a particular service
@app.get("/prices/{service_code}")
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

# Define the route to get all services available in a region
@app.get("/services/")
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


# Custom exception handler to return a 404 response
@app.exception_handler(HTTPException)
async def not_found_exception_handler(request, exc):
    return JSONResponse(content={"detail": "Not Found"}, status_code=404)