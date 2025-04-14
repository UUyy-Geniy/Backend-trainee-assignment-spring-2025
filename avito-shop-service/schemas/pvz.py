from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic.types import UUID
from schemas.reception import ReceptionWithProductsResponse


class City(str, Enum):
    MOSCOW = "Москва"
    SPB = "Санкт-Петербург"
    KAZAN = "Казань"


class PVZCreateRequest(BaseModel):
    city: City


class PVZResponse(PVZCreateRequest):
    id: UUID
    registration_date: datetime
    moderator_id: UUID
    receptions: list[ReceptionWithProductsResponse] = []


class DeleteLastProductResponse(BaseModel):
    status: str


class PVZToDelete(BaseModel):
    id: UUID
