from typing import Optional

from models import users
from repository.base import BaseRepository
from security import get_password_hash
from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncConnection


class UserRepository(BaseRepository[Table]):
    def __init__(self, conn: AsyncConnection):
        super().__init__(users, conn)

    def _before_creation(self, **kwargs):
        kwargs["password_hash"] = get_password_hash(kwargs["password_hash"])
        return kwargs

    async def create_user(self, email: str, password: str, role: str) -> dict:
        return await self.create(
            email=email,
            password_hash=password,
            role=role,
        )

    async def get_by_email(self, email: str) -> Optional[dict]:
        return await self.get(users.c.email == email)
