from contextlib import asynccontextmanager
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from services.pvz import PVZService
from sqlalchemy import column, table


@asynccontextmanager
async def dummy_atomic():
    yield


class DummyUOW:
    pass


@pytest.fixture
def mock_uow():
    uow = DummyUOW()
    uow.atomic = dummy_atomic
    uow.pvz = AsyncMock()
    return uow


test_create_pvz_cases = [
    {
        "name": "success-moscow",
        "city": "Москва",
        "moderator_id": "mod1",
        "expected_error": None,
    },
    {
        "name": "invalid-city",
        "city": "Новосибирск",
        "moderator_id": "mod1",
        "expected_error": ValueError,
    },
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_create_pvz_cases, ids=[c["name"] for c in test_create_pvz_cases])
async def test_create_pvz(mock_uow, case):
    service = PVZService(mock_uow)

    if case["expected_error"]:
        mock_uow.pvz.create_pvz.side_effect = case["expected_error"]("Invalid city")
        with pytest.raises(case["expected_error"]):
            await service.create_pvz(case["city"], case["moderator_id"])
    else:
        result = await service.create_pvz(case["city"], case["moderator_id"])
        assert result is not None
        mock_uow.pvz.create_pvz.assert_awaited_once_with(case["city"], case["moderator_id"])


##########################################################################
# Фикстура для тестов метода get_pvz_list, где требуются таблицы с нужными методами SQLAlchemy
##########################################################################


@pytest.fixture
def mock_uow_with_tables():
    uow = DummyUOW()
    uow.atomic = dummy_atomic

    pvz_table = table(
        "pvz",
        column("id"),
        column("registration_date"),
        column("city"),
        column("moderator_id"),
    )

    receptions_table = table(
        "receptions",
        column("id"),
        column("date_time"),
        column("status"),
        column("pvz_id"),
    )

    products_table = table(
        "products",
        column("id"),
        column("date_time"),
        column("type"),
        column("reception_id"),
        column("removed"),
        column("removal_order"),
    )

    # Присваиваем таблицы соответствующим репозиториям
    uow.pvz = type("DummyRepo", (), {"table": pvz_table})
    uow.receptions = type("DummyRepo", (), {"table": receptions_table})
    uow.products = type("DummyRepo", (), {"table": products_table})

    # Мокаем подключение, которое используется для выполнения запроса.
    uow.conn = AsyncMock()

    # Создаем фиктивный результат, имитирующий поведение SQLAlchemy.
    class DummyResult:
        def mappings(self):
            return self

        def all(self):
            # Возвращаем фиктивный список записей, соответствующий ожидаемой структуре
            return [
                {
                    "id": 1,
                    "registration_date": "2023-01-01",
                    "city": "Москва",
                    "moderator_id": "mod1",
                    "receptions": [],
                }
            ]

    uow.conn.execute.return_value = DummyResult()

    return uow


@pytest.mark.asyncio
async def test_get_pvz_list(mock_uow_with_tables):
    service = PVZService(mock_uow_with_tables)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    page = 1
    limit = 10

    result = await service.get_pvz_list(start_date, end_date, page, limit)
    assert isinstance(result, list)
    expected = [
        {
            "id": 1,
            "registration_date": "2023-01-01",
            "city": "Москва",
            "moderator_id": "mod1",
            "receptions": [],
        }
    ]
    assert result == expected
