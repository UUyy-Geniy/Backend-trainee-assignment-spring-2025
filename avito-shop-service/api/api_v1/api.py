from fastapi import APIRouter

from .endpoints import user, auth, system

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(user.router, tags=["User"])
api_router.include_router(system.router, tags=["System"])