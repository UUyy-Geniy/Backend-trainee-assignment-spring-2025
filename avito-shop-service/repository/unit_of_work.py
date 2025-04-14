from contextlib import asynccontextmanager

from repository.products import ProductRepository
from repository.pvz import PVZRepository
from repository.receptions import ReceptionRepository
from repository.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncConnection


class UnitOfWork:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn
        self.users = UserRepository(conn)
        self.pvz = PVZRepository(conn)
        self.receptions = ReceptionRepository(conn)
        self.products = ProductRepository(conn)

    @asynccontextmanager
    async def atomic(self):
        async with self.conn.begin() as transaction:
            try:
                yield
                await transaction.commit()
            except Exception:
                await transaction.rollback()
                raise
