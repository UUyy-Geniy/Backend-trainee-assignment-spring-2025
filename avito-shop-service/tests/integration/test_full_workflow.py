import pytest
from models import metadata
from repository.unit_of_work import UnitOfWork
from services.auth import AuthService
from services.products import ProductService
from services.pvz import PVZService
from services.receptions import ReceptionService
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


@pytest.mark.integration
async def test_full_workflow(postgres_url):
    engine = create_async_engine(postgres_url)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    try:
        async with AsyncSession(engine) as session:
            uow = UnitOfWork(session)

            # 1. Create moderator и получаем его UUID через токен
            auth_service = AuthService(uow)
            moderator_token = await auth_service.dummy_login("moderator")

            # Импорт decode_token делается здесь, а не на уровне модуля,
            # чтобы избежать проблем с порядком инициализации зависимостей.
            # Например, decode_token может зависеть от конфигурации безопасности,
            # которая должна быть загружена после настройки тестового окружения.
            from security import decode_token

            token_data = decode_token(moderator_token)
            moderator_id = token_data["sub"]

            # 2. Create PVZ с валидным moderator_id
            pvz_service = PVZService(uow)
            pvz = await pvz_service.create_pvz("Москва", moderator_id)

            # 3. Start reception
            reception_service = ReceptionService(uow)
            await reception_service.start_reception(pvz["id"])

            # 4. Add 50 products
            product_service = ProductService(uow)
            for _ in range(50):
                await product_service.add_product(pvz["id"], "электроника")

            # 5. Close reception
            closed_reception = await reception_service.close_last_reception(pvz["id"])

            # Assertions
            assert closed_reception["status"] == "close"
            products = await uow.products.get_all_by_receprion_id(reception_id=closed_reception["id"])
            assert len(products) == 50

    finally:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
        await engine.dispose()
