from fastapi import APIRouter
from app.api.v1.endpoints import admin, auth, marketplace, farmers, assistant, educational, recommendations, cart, reviews, weather, prices

api_router = APIRouter()

# Register routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
api_router.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(educational.router, prefix="/educational", tags=["educational"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
