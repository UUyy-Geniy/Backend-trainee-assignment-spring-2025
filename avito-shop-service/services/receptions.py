from exceptions.app_exception import ActiveReceptionExistsError, NoActiveReceptionError
from repository.unit_of_work import UnitOfWork
from metrics.metrics import RECEPTIONS_CREATED

class ReceptionService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow
    
    async def start_reception(self, pvz_id: str) -> dict:
        async with self._uow.atomic():
            active = await self._uow.receptions.get_active_reception(pvz_id)
            if active:
                raise ActiveReceptionExistsError()
                
            result = await self._uow.receptions.create(
                pvz_id=pvz_id,
                status='in_progress'
            )
            RECEPTIONS_CREATED.inc()
            return result
    
    async def close_last_reception(self, pvz_id: str) -> dict:
        async with self._uow.atomic():
            reception = await self._uow.receptions.get_active_reception(pvz_id)
            if not reception:
                raise NoActiveReceptionError()
            
            return await self._uow.receptions.update(
                reception["id"],
                status="close"
            )
