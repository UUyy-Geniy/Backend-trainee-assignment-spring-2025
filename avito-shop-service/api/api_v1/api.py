from fastapi import APIRouter

from .endpoints import auth, receptions, pvz, product

api_router = APIRouter()
api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(product.router, tags=["Product"])
api_router.include_router(receptions.router, tags=["Receptions"])
api_router.include_router(pvz.router, tags=["PVZ"])