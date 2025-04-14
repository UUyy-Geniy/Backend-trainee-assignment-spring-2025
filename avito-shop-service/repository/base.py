from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

TableType = TypeVar("TableType")


class BaseRepository(Generic[TableType]):
    def __init__(self, table: Type[TableType], conn: AsyncConnection):
        self.table = table
        self.conn = conn

    def _before_creation(self, **kwargs) -> dict:
        return kwargs

    async def get(self, *where_clauses, **filter_by) -> Optional[dict]:
        query = select(self.table)

        if where_clauses:
            query = query.where(*where_clauses)
        if filter_by:
            query = query.filter_by(**filter_by)

        result = await self.conn.execute(query)
        return result.mappings().first()

    async def get_by_id(self, _id: Any) -> Optional[dict]:
        return await self.get(self.table.c.id == _id)

    async def create(self, **data) -> dict:
        data = self._before_creation(**data)
        query = insert(self.table).values(**data).returning(self.table)
        result = await self.conn.execute(query)
        return result.mappings().first()

    async def update(self, _id: Any, **data) -> bool:
        query = update(self.table).where(self.table.c.id == _id).values(**data).returning(self.table)
        result = await self.conn.execute(query)
        return result.mappings().first()

    async def delete(self, _id: Any) -> bool:
        query = delete(self.table).where(self.table.c.id == _id)
        result = await self.conn.execute(query)
        return result.rowcount > 0
