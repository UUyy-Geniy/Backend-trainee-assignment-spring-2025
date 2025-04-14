from exceptions.app_exception import ActiveReceptionExistsError, NoActiveReceptionError, PVZNotFoundError
from metrics.metrics import RECEPTIONS_CREATED
from repository.unit_of_work import UnitOfWork


class ReceptionService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def start_reception(self, pvz_id: str) -> dict:
        async with self._uow.atomic():
            pvz = await self._uow.pvz.get_by_id(pvz_id)
            if not pvz:
                raise PVZNotFoundError()

            active = await self._uow.receptions.get_active_reception(pvz_id)
            if active:
                raise ActiveReceptionExistsError()

            result = await self._uow.receptions.create(pvz_id=pvz_id, status="in_progress")
            RECEPTIONS_CREATED.inc()
            return result

    async def close_last_reception(self, pvz_id: str) -> dict:
        async with self._uow.atomic():
            pvz = await self._uow.pvz.get_by_id(pvz_id)
            if not pvz:
                raise PVZNotFoundError()

            reception = await self._uow.receptions.get_active_reception(pvz_id)
            if not reception:
                raise NoActiveReceptionError()

            return await self._uow.receptions.update(reception["id"], status="close")
