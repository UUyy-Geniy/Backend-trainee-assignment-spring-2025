from repository.unit_of_work import UnitOfWork
from datetime import datetime
from sqlalchemy import select, func, text
from metrics.metrics import PVZ_CREATED
import logging

class PVZService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    async def create_pvz(self, city: str, moderator_id: str) -> dict:
        async with self._uow.atomic():
            result = await self._uow.pvz.create_pvz(city, moderator_id)
            PVZ_CREATED.inc()
            return result
    
    async def get_all_pvz(self) -> list[dict]:
        async with self._uow.atomic():
            return await self._uow.pvz.get_all_pvz()
    
    async def get_pvz_list(
        self,
        start_date: datetime | None,
        end_date: datetime | None,
        page: int,
        limit: int
    ) -> list[dict]:
        async with self._uow.atomic():
            pvz = self._uow.pvz.table
            receptions = self._uow.receptions.table
            products = self._uow.products.table

            empty_json_array = text("'[]'::jsonb")

            products_subq = (
                select(
                    products.c.reception_id,
                    func.coalesce(
                        func.jsonb_agg(
                            func.jsonb_build_object(
                                'id', products.c.id,
                                'date_time', products.c.date_time,
                                'type', products.c.type,
                                'reception_id', products.c.reception_id,
                                'removed', products.c.removed,
                                'removal_order', products.c.removal_order
                            )
                        ),
                        empty_json_array
                    ).label('products')
                )
                .group_by(products.c.reception_id)
                .where(products.c.removed == False)
                .subquery()
            )

            receptions_subq = (
                select(
                    receptions.c.id,
                    receptions.c.date_time,
                    receptions.c.status,
                    receptions.c.pvz_id,
                    func.coalesce(products_subq.c.products, empty_json_array).label('products')
                )
                .select_from(
                    receptions.outerjoin(
                        products_subq,
                        receptions.c.id == products_subq.c.reception_id
                    )
                )
                .where(receptions.c.id.is_not(None))
                .subquery()
            )

            query = (
                select(
                    pvz.c.id,
                    pvz.c.registration_date,
                    pvz.c.city,
                    pvz.c.moderator_id,
                    func.coalesce(
                        func.jsonb_agg(
                            func.jsonb_build_object(
                                'id', receptions_subq.c.id,
                                'date_time', receptions_subq.c.date_time,
                                'status', receptions_subq.c.status,
                                'pvz_id', receptions_subq.c.pvz_id,
                                'products', receptions_subq.c.products
                            )
                        ).filter(receptions_subq.c.id.is_not(None)),
                        empty_json_array
                    ).label('receptions')
                )
                .select_from(
                    pvz.outerjoin(
                        receptions_subq,
                        pvz.c.id == receptions_subq.c.pvz_id
                    )
                )
                .group_by(pvz.c.id)
            )

            if start_date and end_date:
                query = query.where(
                    pvz.c.registration_date.between(start_date, end_date)
                )
            
            query = query.offset((page - 1) * limit).limit(limit)
            result = await self._uow.conn.execute(query)
            rows = result.mappings().all()
            return rows