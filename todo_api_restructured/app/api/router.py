from fastapi import APIRouter

from app.api.endpoints import auth, admin, user

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
