from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from api.models import ProductFamily, Product, Price
from api.routers import product_family, services, products, prices

# Create a FastAPI instance
api = FastAPI()

# Include the router from the route module
api.include_router(product_family.router, prefix="/api")
api.include_router(services.router, prefix="/api")
api.include_router(products.router, prefix="/api")
api.include_router(prices.router, prefix="/api")

# Custom exception handler to return a 404 response
@api.exception_handler(HTTPException)
async def not_found_exception_handler(request, exc):
    return JSONResponse(content={"detail": "Not Found"}, status_code=404)