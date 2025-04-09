from fastapi import APIRouter
from tasks.scheduler import scheduler
from pydantic import BaseModel

router = APIRouter()

class SchedulerJob(BaseModel):
    id: str
    name: str
    next_run: str | None
    trigger: str

@router.get("/system/scheduler/jobs", response_model=list[SchedulerJob])
async def get_scheduler_jobs():
    return [
        SchedulerJob(
            id=job.id,
            name=job.name,
            next_run=str(job.next_run_time),
            trigger=str(job.trigger)
        )
        for job in scheduler.scheduler.get_jobs()
    ]