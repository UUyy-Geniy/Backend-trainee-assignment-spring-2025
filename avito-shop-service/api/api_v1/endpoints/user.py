from fastapi import APIRouter, Depends, Path, status
from typing import Annotated

from api.deps import get_current_user, get_user_service
from services.user import UserService

router = APIRouter()
