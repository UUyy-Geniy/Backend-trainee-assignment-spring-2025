import pytest
from unittest.mock import AsyncMock
from contextlib import asynccontextmanager
from uuid import uuid4

from services.auth import AuthService
from exceptions.app_exception import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError
from security import get_password_hash

@asynccontextmanager
async def dummy_atomic():
    yield

@pytest.fixture
def mock_uow():
    mock = AsyncMock()
    mock.atomic = dummy_atomic
    return mock

test_dummy_login_cases = [
    {
        "name": "success-employee",
        "role": "employee",
        "expected_role": "employee",
        "expected_error": None
    },
    {
        "name": "success-moderator",
        "role": "moderator",
        "expected_role": "moderator",
        "expected_error": None
    }
]

test_register_cases = [
    {
        "name": "success",
        "email": "new@test.com",
        "password": "pass",
        "role": "employee",
        "db_response": None,
        "expected_error": None
    },
    {
        "name": "user-exists",
        "email": "exists@test.com",
        "password": "pass",
        "role": "employee",
        "db_response": {"id": 1},
        "expected_error": UserAlreadyExistsError
    }
]

test_login_cases = [
    {
        "name": "success",
        "email": "valid@test.com",
        "password": "correct",
        "db_user": {"id": 1, "password_hash": get_password_hash("correct"), "role": "employee"},
        "expected_error": None
    },
    {
        "name": "user-not-found",
        "email": "nonexist@test.com",
        "password": "any",
        "db_user": None,
        "expected_error": UserNotFoundError
    },
    {
        "name": "invalid-password",
        "email": "valid@test.com",
        "password": "wrong",
        "db_user": {"id": 1, "password_hash": get_password_hash("correct"), "role": "employee"},
        "expected_error": InvalidCredentialsError
    }
]

@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_dummy_login_cases, ids=[c["name"] for c in test_dummy_login_cases])
async def test_dummy_login(mock_uow, case):
    auth_service = AuthService(mock_uow)
    
    mock_uow.users.create_user.return_value = {"id": 1, "role": case["role"]}
    
    result = await auth_service.dummy_login(case["role"])
    
    assert isinstance(result, str)
    assert len(result.split(".")) == 3

    mock_uow.users.create_user.assert_awaited_once()
    args, kwargs = mock_uow.users.create_user.call_args
    assert kwargs["role"] == case["role"]
    assert "dummy_" in kwargs["email"]
    assert isinstance(kwargs["password"], str)

@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_register_cases, ids=[c["name"] for c in test_register_cases])
async def test_register_user(mock_uow, case):

    mock_uow.users.get_by_email.return_value = case["db_response"]
    auth_service = AuthService(mock_uow)
    
    if case["expected_error"]:
        with pytest.raises(case["expected_error"]):
            await auth_service.register_user(case["email"], case["password"], case["role"])
    else:
        result = await auth_service.register_user(case["email"], case["password"], case["role"])
        assert result is not None
        mock_uow.users.create_user.assert_awaited_once()

@pytest.mark.asyncio
@pytest.mark.parametrize("case", test_login_cases, ids=[c["name"] for c in test_login_cases])
async def test_login_user(mock_uow, case):
    mock_uow.users.get_by_email.return_value = case["db_user"]
    auth_service = AuthService(mock_uow)
    
    if case["expected_error"]:
        with pytest.raises(case["expected_error"]):
            await auth_service.login_user(case["email"], case["password"])
    else:
        token = await auth_service.login_user(case["email"], case["password"])
        assert isinstance(token, str)
        # Проверяем, что токен соответствует формату JWT
        assert len(token.split(".")) == 3
