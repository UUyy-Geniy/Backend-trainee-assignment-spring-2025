import logging
from contextlib import asynccontextmanager

from core.config import settings
from exceptions.middleware import ErrorHandlingMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router
from tasks.scheduler import scheduler, setup_scheduler

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    if settings.SCHEDULER_ENABLED:
        try:
            setup_scheduler()
            await scheduler.start()
            logger.info("Scheduler started with jobs: %s", 
                        [job.name for job in scheduler.list_jobs()])
        except Exception as e:
            logger.error("Scheduler initialization failed: %s", str(e))
            raise
    
    yield
    logger.info("Stopping application...")
    
    if settings.SCHEDULER_ENABLED and scheduler.scheduler.running:
        try:
            await scheduler.shutdown()
            logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error("Scheduler shutdown error: %s", str(e))

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
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