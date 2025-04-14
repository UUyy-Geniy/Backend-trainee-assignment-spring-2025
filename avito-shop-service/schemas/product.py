from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic.types import UUID


class ProductType(str, Enum):
    ELECTRONICS = "электроника"
    CLOTHES = "одежда"
    SHOES = "обувь"


class ProductRequest(BaseModel):
    type: ProductType
    pvz_id: UUID


class ProductResponse(BaseModel):
    id: UUID
    date_time: datetime
    type: ProductType
    reception_id: UUID
    removed: bool
    removal_order: int
