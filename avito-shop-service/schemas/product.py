from pydantic import BaseModel
from pydantic.types import UUID
from enum import Enum
from datetime import datetime

class ProductType(str, Enum):
    ELECTRONICS = "электроника"
    CLOTHES = "одежда"
    SHOES = "обувь"

class ProductRequest(BaseModel):
    type: ProductType
    pvz_id: str

class ProductResponse(BaseModel):
    id: UUID
    date_time: datetime
    type: ProductType
    reception_id: UUID
    removed: bool
    removal_order: int