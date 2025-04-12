from models import pvz
from repository.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import Table

class PVZRepository(BaseRepository[Table]):
    def __init__(self, conn: AsyncConnection):
        super().__init__(pvz, conn)
        
    async def create_pvz(self, city: str, moderator_id: str) -> dict:
        return await self.create(
            city=city,
            moderator_id=moderator_id
        )