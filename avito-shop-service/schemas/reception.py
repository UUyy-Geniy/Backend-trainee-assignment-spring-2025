from pydantic import BaseModel, Field
from pydantic.types import UUID
from datetime import datetime
from schemas.product import ProductResponse

class ReceptionRequest(BaseModel):
    pvz_id: UUID

class ReceptionResponse(BaseModel):
    id: UUID
    date_time: datetime
    pvz_id: UUID
    status: str

class ReceptionWithProductsResponse(ReceptionResponse):
    products: list[ProductResponse]
