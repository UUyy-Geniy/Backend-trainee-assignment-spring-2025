from api.deps import get_current_employee, get_reception_service
from fastapi import APIRouter, Depends, status
from services.receptions import ReceptionService

router = APIRouter(prefix="/receptions")


@router.post("", status_code=status.HTTP_201_CREATED)
async def start_reception(
    pvz_id: str,
    employee: dict = Depends(get_current_employee),
    service: ReceptionService = Depends(get_reception_service),
):
    reception = await service.start_reception(pvz_id)
    return {"id": reception["id"]}
