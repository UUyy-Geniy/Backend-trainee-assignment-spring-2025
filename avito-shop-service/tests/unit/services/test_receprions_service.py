import pytest
from unittest.mock import AsyncMock, MagicMock
from services.receptions import ReceptionService
from exceptions.app_exception import ActiveReceptionExistsError, NoActiveReceptionError
from contextlib import asynccontextmanager

@asynccontextmanager
async def dummy_atomic():
    yield

@pytest.fixture
def mock_uow():
    mock = AsyncMock()
    mock.atomic = dummy_atomic
    return mock

test_start_reception_cases = [
    {
        "name": "success",
        "pvz_id": "pvz1",
        "active_reception": None,
        "expected_status": "in_progress",
        "expected_error": None
    },
    {
        "name": "active-exists",
        "pvz_id": "pvz2",
        "active_reception": {"id": "rec1", "status": "in_progress"},
        "expected_error": ActiveReceptionExistsError
    }
]

test_close_reception_cases = [
    {
        "name": "success",
        "pvz_id": "pvz1",
        "active_reception": {"id": "rec1", "status": "in_progress"},
        "expected_status": "close",
        "expected_error": None
    },
    {
        "name": "no-active",
        "pvz_id": "pvz2",
        "active_reception": None,
        "expected_error": NoActiveReceptionError
    }
]

@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_start_reception_cases, ids=[c["name"] for c in test_start_reception_cases])
async def test_start_reception(mock_uow, case):
    service = ReceptionService(mock_uow)
    mock_uow.receptions.get_active_reception.return_value = case["active_reception"]
    
    if case["active_reception"]:
        mock_uow.receptions.create.side_effect = Exception("Should not be called")
    else:
        mock_uow.receptions.create.return_value = {"id": "new_rec", "status": "in_progress"}

    if case["expected_error"]:
        with pytest.raises(case["expected_error"]):
            await service.start_reception(case["pvz_id"])
    else:
        result = await service.start_reception(case["pvz_id"])
        
        assert result["status"] == case["expected_status"]
        mock_uow.receptions.get_active_reception.assert_awaited_once_with(case["pvz_id"])
        mock_uow.receptions.create.assert_awaited_once_with(
            pvz_id=case["pvz_id"],
            status="in_progress"
        )

@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_close_reception_cases, ids=[c["name"] for c in test_close_reception_cases])
async def test_close_last_reception(mock_uow, case):
    service = ReceptionService(mock_uow)
    mock_uow.receptions.get_active_reception.return_value = case["active_reception"]
    
    if case["active_reception"]:
        mock_uow.receptions.update.return_value = {"id": case["active_reception"]["id"], "status": "close"}
    else:
        mock_uow.receptions.update.side_effect = Exception("Should not be called")

    if case["expected_error"]:
        with pytest.raises(case["expected_error"]):
            await service.close_last_reception(case["pvz_id"])
    else:
        result = await service.close_last_reception(case["pvz_id"])
        
        assert result["status"] == case["expected_status"]
        mock_uow.receptions.get_active_reception.assert_awaited_once_with(case["pvz_id"])
        mock_uow.receptions.update.assert_awaited_once_with(
            case["active_reception"]["id"],
            status="close"
        )