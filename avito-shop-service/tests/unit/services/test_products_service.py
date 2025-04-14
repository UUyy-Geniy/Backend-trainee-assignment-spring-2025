from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
from exceptions.app_exception import NoActiveReceptionError, NoProductToDeleteError
from services.products import ProductService


@asynccontextmanager
async def dummy_atomic():
    yield


@pytest.fixture
def mock_uow():
    mock = AsyncMock()
    mock.atomic = dummy_atomic
    return mock


test_add_product_cases = [
    {
        "name": "success-first-product",
        "pvz_id": "pvz1",
        "product_type": "электроника",
        "reception_exists": True,
        "last_product": None,
        "expected_order": 1,
        "expected_error": None,
    },
    {
        "name": "success-next-product",
        "pvz_id": "pvz1",
        "product_type": "одежда",
        "reception_exists": True,
        "last_product": {"removal_order": 3},
        "expected_order": 4,
        "expected_error": None,
    },
    {
        "name": "no-active-reception",
        "pvz_id": "pvz2",
        "product_type": "обувь",
        "reception_exists": False,
        "last_product": None,
        "expected_error": NoActiveReceptionError,
    },
]

test_delete_product_cases = [
    {
        "name": "success",
        "pvz_id": "pvz1",
        "reception_exists": True,
        "last_product": {"id": 1, "removed": False},
        "expected_result": True,
        "expected_error": None,
    },
    {
        "name": "no-active-reception",
        "pvz_id": "pvz2",
        "reception_exists": False,
        "last_product": None,
        "expected_error": NoActiveReceptionError,
    },
    {
        "name": "no-products",
        "pvz_id": "pvz1",
        "reception_exists": True,
        "last_product": None,
        "expected_error": NoProductToDeleteError,
    },
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_add_product_cases, ids=[c["name"] for c in test_add_product_cases])
async def test_add_product(mock_uow, case):
    mock_uow.receptions.get_active_reception.return_value = {"id": "reception1"} if case["reception_exists"] else None
    mock_uow.products.get_last_product.return_value = case["last_product"]
    mock_uow.products.create.return_value = {"id": 1}

    service = ProductService(mock_uow)

    if case["expected_error"]:
        with pytest.raises(case["expected_error"]):
            await service.add_product(case["pvz_id"], case["product_type"])
    else:
        result = await service.add_product(case["pvz_id"], case["product_type"])
        assert result is not None
        mock_uow.products.create.assert_awaited_once_with(
            reception_id="reception1",
            type=case["product_type"],
            removal_order=case["expected_order"],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    test_delete_product_cases,
    ids=[c["name"] for c in test_delete_product_cases],
)
async def test_delete_product(mock_uow, case):
    mock_uow.receptions.get_active_reception.return_value = {"id": "reception1"} if case["reception_exists"] else None
    mock_uow.products.get_last_active_product.return_value = case["last_product"]
    mock_uow.products.remove.return_value = True

    service = ProductService(mock_uow)

    if case["expected_error"]:
        with pytest.raises(case["expected_error"]):
            await service.delete_last_product(case["pvz_id"])
    else:
        result = await service.delete_last_product(case["pvz_id"])
        assert result is True
        mock_uow.products.remove.assert_awaited_once_with(case["last_product"]["id"])
