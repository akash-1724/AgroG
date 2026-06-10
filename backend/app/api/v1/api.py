from app.api.v1.endpoints import auth, marketplace, farmers, assistant, educational, recommendations

api_router = APIRouter()

# Register routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
api_router.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(educational.router, prefix="/educational", tags=["educational"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
