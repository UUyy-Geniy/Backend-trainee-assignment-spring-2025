from pydantic import BaseModel, Field
from pydantic.types import UUID
from datetime import datetime
from enum import Enum
from schemas.reception import ReceptionWithProductsResponse


class City(str, Enum):
    MOSCOW = "Москва"
    SPB = "Санкт-Петербург"
    KAZAN = "Казань"

class PVZCreateRequest(BaseModel):
    city : City

class PVZResponse(PVZCreateRequest):
    id: UUID
    registration_date: datetime
    moderator_id: UUID
    receptions: list[ReceptionWithProductsResponse] = []

class PVZToDelete(BaseModel):
    id: UUID