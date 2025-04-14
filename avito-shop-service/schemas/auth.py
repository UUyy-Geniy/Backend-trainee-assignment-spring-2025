from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    employee = "employee"
    moderator = "moderator"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    token: str


class DummyLoginRequest(BaseModel):
    role: Role


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: Role


class LoginRequest(BaseModel):
    email: str
    password: str
