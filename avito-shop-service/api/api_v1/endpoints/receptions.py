from api.deps import get_current_employee, get_reception_service
from fastapi import APIRouter, Depends, status
from schemas.reception import ReceptionCreateResponse, ReceptionRequest
from services.receptions import ReceptionService

router = APIRouter(prefix="/receptions")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ReceptionCreateResponse)
async def start_reception(
    reception_create: ReceptionRequest,
    employee: dict = Depends(get_current_employee),
    service: ReceptionService = Depends(get_reception_service),
):
    reception = await service.start_reception(reception_create.pvz_id)
    return ReceptionCreateResponse(id=reception["id"])
