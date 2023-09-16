from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.routers import product_family, services, products, prices
from api.utils.customHTTPException import CustomHTTPException

# Create a FastAPI instance
api = FastAPI()

# Include the router from the route module
api.include_router(product_family.router, prefix="/api")
api.include_router(services.router, prefix="/api")
api.include_router(products.router, prefix="/api")
api.include_router(prices.router, prefix="/api")


# Custom exception handler to return a 404 response
@api.exception_handler(CustomHTTPException)
async def custom_exception_handler(request, exc):
    if exc.status_code and exc.detail:
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)
    else:
        return JSONResponse(content={"detail": "Not Found"}, status_code=404)
