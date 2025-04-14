from models import pvz
from repository.base import BaseRepository
from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncConnection


class PVZRepository(BaseRepository[Table]):
    def __init__(self, conn: AsyncConnection):
        super().__init__(pvz, conn)

    async def create_pvz(self, city: str, moderator_id: str) -> dict:
        return await self.create(city=city, moderator_id=moderator_id)

    async def get_all_pvz(self):
        query = select(self.table)
        result = await self.conn.execute(query)
        return result.mappings().all()
