from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.types import UUID


class UserBase(BaseModel):
    email: str = Field(..., example="user@example.com")
    role: str = Field(..., example="employee")


class UserCreate(UserBase):
    password: str = Field(..., example="secret")


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
