from repository.unit_of_work import UnitOfWork
from exceptions.app_exception import NoActiveReceptionError, NoProductToDeleteError

class ProductService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def add_product(self, pvz_id: str, product_type: str) -> dict:
        async with self._uow.atomic():
            reception = await self._uow.receptions.get_active_reception(pvz_id)
            if not reception:
                raise NoActiveReceptionError()
            
            last_product = await self._uow.products.get_last_product(reception['id'])
            next_order = (last_product['removal_order'] + 1) if last_product else 1
            
            return await self._uow.products.create(
                reception_id=reception['id'],
                type=product_type,
                removal_order=next_order
            )

    async def delete_last_product(self, pvz_id: str) -> bool:
        async with self._uow.atomic():
            reception = await self._uow.receptions.get_active_reception(pvz_id)
            if not reception:
                raise NoActiveReceptionError()
            
            product = await self._uow.products.get_last_active_product(reception['id'])
            if not product:
                raise NoProductToDeleteError()
                
            return await self._uow.products.remove(product['id'])