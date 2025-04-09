from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from core.config import settings
from repository.unit_of_work import UnitOfWork
from exceptions.app_exception import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError
)
from security import verify_password
import secrets
from uuid import uuid4

class AuthService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def register_user(self, email: str, password: str, role: str) -> dict:
        async with self._uow.atomic():
            if await self._uow.users.get_by_email(email):
                raise UserAlreadyExistsError(email=email)
                
            return await self._uow.users.create_user(email, password, role)

    async def dummy_login(self, role: str) -> str:
        async with self._uow.atomic():
            email = f"dummy_{secrets.token_hex(8)}@example.com"
            user = await self._uow.users.create_user(
                email=email,
                password=secrets.token_urlsafe(32),
                role=role
            )
            
            token = secrets.token_urlsafe(64)
            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            await self._uow.auth_token.create_token(
                user_id=str(user["id"]),
                token=token,
                expires_at=expires_at
            )
            return token

    async def login_user(self, email: str, password: str) -> str:
        async with self._uow.atomic():
            user = await self._uow.users.get_by_email(email)
            if not user:
                raise UserNotFoundError()

            if not verify_password(password, user["password_hash"]):
                raise InvalidCredentialsError()

            token = secrets.token_urlsafe(64)
            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            await self._uow.auth_token.create_token(
                user_id=str(user["id"]),
                token=token,
                expires_at=expires_at
            )
            return token
    
    async def delete_expired_tokens(self):
        return await self._uow.auth_token.delete_expired()
