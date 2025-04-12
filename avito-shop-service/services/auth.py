from datetime import datetime, timedelta
from jose import jwt
from core.config import settings
from repository.unit_of_work import UnitOfWork
from exceptions.app_exception import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError
)
from security import verify_password

from uuid import uuid4

class AuthService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def dummy_login(self, role: str) -> str:
        async with self._uow.atomic():
            email = f"dummy_{uuid4()}@example.com"
            user = await self._uow.users.create_user(
                email=email,
                password=str(uuid4()),
                role=role
            )
            
            return self._create_access_token(str(user["id"]), user["role"])

    async def register_user(self, email: str, password: str, role: str) -> dict:
        async with self._uow.atomic():
            if await self._uow.users.get_by_email(email):
                raise UserAlreadyExistsError(email=email)
                
            return await self._uow.users.create_user(email, password, role)

    async def login_user(self, email: str, password: str) -> str:
        async with self._uow.atomic():
            user = await self._uow.users.get_by_email(email)
            if not user:
                raise UserNotFoundError()
            if not verify_password(password, user["password_hash"]):
                raise InvalidCredentialsError()
                
            return self._create_access_token(str(user["id"]), user["role"])

    def _create_access_token(self, user_id: str, role: str) -> str:
        expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "role": role,
            "exp": expires
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
