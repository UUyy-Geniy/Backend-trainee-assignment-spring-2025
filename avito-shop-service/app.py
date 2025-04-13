import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.api_v1.api import api_router
from exceptions.middleware import ErrorHandlingMiddleware
from metrics.middleware import add_metrics_middleware
from prometheus_client import start_http_server

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
app.middleware("http")(add_metrics_middleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

async def start_metrics_server(port=9000):
    start_http_server(port)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_metrics_server(9000))