from models import products
from repository.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import Optional
from sqlalchemy import select, update

class ProductRepository(BaseRepository):
    def __init__(self, conn: AsyncConnection):
        super().__init__(products, conn)
    
    async def get_last_product(self, reception_id: str) -> Optional[dict]:
        query = select(self.table).where(
            self.table.c.reception_id == reception_id
        ).order_by(self.table.c.removal_order.desc()).limit(1)
        result = await self.conn.execute(query)
        return result.mappings().first()
    
    async def get_last_active_product(self, reception_id: str) -> Optional[dict]:
        query = select(self.table).where(
            (self.table.c.reception_id == reception_id) &
            (self.table.c.removed == False)
        ).order_by(self.table.c.removal_order.desc()).limit(1)
        result = await self.conn.execute(query)
        return result.mappings().first()
    
    async def remove(self, product_id: str) -> bool:
        query = update(self.table).where(self.table.c.id == product_id).values(removed=True)
        result = await self.conn.execute(query)
        return result.rowcount > 0