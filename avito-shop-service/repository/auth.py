from datetime import datetime
from models import auth_tokens
from sqlalchemy import and_, Table
from sqlalchemy.ext.asyncio import AsyncConnection
from repository.base import BaseRepository
from typing import Optional

class AuthRepository(BaseRepository[Table]):
    def __init__(self, conn: AsyncConnection):
        super().__init__(auth_tokens, conn)

    async def create_token(self, user_id: str, token: str, expires_at: datetime) -> dict:
        return await self.create(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )

    async def get_valid_token(self, token: str) -> Optional[dict]:
        return await self.get(
            and_(
                self.table.c.token == token,
                self.table.c.expires_at > datetime.now()
            )
        )