from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncConnection

from repository.user import UserRepository
from repository.auth import AuthRepository

class UnitOfWork:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn
        self.users = UserRepository(conn)
        self.auth = AuthRepository(conn)

    @asynccontextmanager
    async def atomic(self):
        async with self.conn.begin() as transaction:
            try:
                yield
                await transaction.commit()
            except Exception:
                await transaction.rollback()
                raise