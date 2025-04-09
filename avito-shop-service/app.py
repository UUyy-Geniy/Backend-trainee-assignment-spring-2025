import logging

from core.config import settings
from exceptions.middleware import ErrorHandlingMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ErrorHandlingMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)
