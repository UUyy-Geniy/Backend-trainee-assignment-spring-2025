from typing import Optional

from models import receptions
from repository.base import BaseRepository
from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncConnection


class ReceptionRepository(BaseRepository[Table]):
    def __init__(self, conn: AsyncConnection):
        super().__init__(receptions, conn)

    async def get_active_reception(self, pvz_id: str) -> Optional[dict]:
        query = select(self.table).where((self.table.c.pvz_id == pvz_id) & (self.table.c.status == "in_progress"))
        result = await self.conn.execute(query)
        return result.mappings().first()
