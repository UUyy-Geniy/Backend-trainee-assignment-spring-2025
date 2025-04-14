from datetime import datetime

from pydantic import BaseModel
from pydantic.types import UUID
from schemas.product import ProductResponse


class ReceptionRequest(BaseModel):
    pvz_id: UUID


class ReceptionCreateResponse(BaseModel):
    id: UUID


class ReceptionResponse(BaseModel):
    id: UUID
    date_time: datetime
    pvz_id: UUID
    status: str


class ReceptionWithProductsResponse(ReceptionResponse):
    products: list[ProductResponse]
