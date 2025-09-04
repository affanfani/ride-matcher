from fastapi import APIRouter
from app.api.routes import rides, auth

# API Router with prefix
api_router = APIRouter(prefix="/api/v1")

# Include routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(rides.router, prefix="/rides", tags=["rides"])

# Security check endpoint
@api_router.get("/health")
async def api_health():
    """API health check endpoint"""
    return {"status": "API is running", "version": "1.0.0"}
