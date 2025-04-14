from datetime import datetime, timedelta
from uuid import UUID

from api.deps import (
    get_current_employee,
    get_current_moderator,
    get_current_staff,
    get_product_service,
    get_pvz_service,
    get_reception_service,
)
from fastapi import APIRouter, Depends, Query, status
from schemas.pvz import PVZCreateRequest, PVZResponse
from schemas.reception import ReceptionResponse
from services.products import ProductService
from services.pvz import PVZService
from services.receptions import ReceptionService

router = APIRouter(prefix="/pvz")


@router.post("", response_model=PVZResponse, status_code=status.HTTP_201_CREATED)
async def create_pvz(
    request: PVZCreateRequest,
    moderator: dict = Depends(get_current_moderator),
    service: PVZService = Depends(get_pvz_service),
):
    pvz = await service.create_pvz(request.city, moderator.id)
    return pvz


@router.get("", response_model=list[PVZResponse])
async def get_pvz_list(
    start_date: datetime | None = Query(default=datetime.now() - timedelta(days=7)),
    end_date: datetime | None = Query(default=datetime.now()),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=30),
    staff: dict = Depends(get_current_staff),
    service: PVZService = Depends(get_pvz_service),
):
    return await service.get_pvz_list(start_date, end_date, page, limit)


@router.post("/{pvz_id}/close_last_reception", response_model=ReceptionResponse)
async def close_last_reception(
    pvz_id: UUID,
    employee: dict = Depends(get_current_employee),
    service: ReceptionService = Depends(get_reception_service),
):
    return await service.close_last_reception(pvz_id)


@router.post("/{pvz_id}/delete_last_product", status_code=status.HTTP_200_OK)
async def delete_last_product(
    pvz_id: UUID,
    employee: dict = Depends(get_current_employee),
    service: ProductService = Depends(get_product_service),
):
    await service.delete_last_product(pvz_id)
    return {"status": "success"}
