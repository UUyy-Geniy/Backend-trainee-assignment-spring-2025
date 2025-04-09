import logging
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from core.config import settings
from repository.unit_of_work import UnitOfWork
from core.engine import get_connection


logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._jobs = []
        self.job_defaults = {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 60
        }
    
    async def start(self):
        if not self.scheduler.running:
            self.scheduler.configure(job_defaults=self.job_defaults)
            self.scheduler.start()
            logger.info("Scheduler started")

    async def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

    def add_job(self, func, **kwargs):
        job = self.scheduler.add_job(func, **kwargs)
        logger.info("Added job: %s", job)
        return job
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        for job in self._jobs:
            try:
                jobs.append({
                    "id": job.id,
                    "name": job.name or "Unnamed",
                    "trigger": str(job.trigger),
                    "next_run": str(job.next_run_time) if job.next_run_time else "None"
                })
            except Exception as e:
                logger.error("Error processing job: %s", str(e))
        return jobs

scheduler = Scheduler()

async def clean_expired_tokens():
    conn = None
    try:
        logger.debug("Starting token cleanup job")
        conn = await get_connection()
        uow = UnitOfWork(conn)
        
        async with uow.atomic():
            result = await uow.auth_token.delete_expired_tokens()
            logger.info("Cleaned expired tokens")
            return result
            
    except Exception as e:
        logger.error("Token cleanup failed: %s", str(e), exc_info=True)
        raise
    finally:
        if conn:
            await conn.close()

def setup_scheduler():
    if not settings.SCHEDULER_ENABLED:
        logger.warning("Scheduler is disabled in config")
        return

    scheduler.add_job(
        clean_expired_tokens,
        trigger=IntervalTrigger(
            minutes=settings.TOKEN_CLEANUP_INTERVAL,
            jitter=30
        ),
        id="token_cleanup",
        name="Clean expired auth tokens",
        replace_existing=True
    )

    logger.info("Scheduler configured with %d jobs", 
               len(scheduler.scheduler.get_jobs()))