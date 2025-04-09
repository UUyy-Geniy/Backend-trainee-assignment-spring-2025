from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    email: str = Field(..., example="user@example.com")
    role: str = Field(..., example="employee")

class UserCreate(UserBase):
    password: str = Field(..., example="secret")

class UserResponse(UserBase):
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True