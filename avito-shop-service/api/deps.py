from typing import Annotated
from datetime import datetime
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncConnection

from core.config import settings
from core.engine import get_connection

from schemas.user import UserResponse
from repository.unit_of_work import UnitOfWork
from services.auth import AuthService
from services.products import ProductService
from services.receptions import ReceptionService
from services.pvz import PVZService
from exceptions.app_exception import InvalidCredentialsError, UserNotFoundError, InsufficientPermissionsError
        
async def get_uow(conn: AsyncConnection = Depends(get_connection)) -> UnitOfWork:
    try:
        yield UnitOfWork(conn)
    finally:
        await conn.close()


def get_auth_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> AuthService:
    return AuthService(uow)

def get_product_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> ProductService:
    return ProductService(uow)

def get_reception_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> ReceptionService:
    return ReceptionService(uow)

def get_pvz_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> PVZService:
    return PVZService(uow)


security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> UserResponse:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if (user_id := payload.get("sub")) is None:
            raise InvalidCredentialsError()
            
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise InvalidCredentialsError("Token expired")
            
    except JWTError as exc:
        raise InvalidCredentialsError() from exc
    async with uow.atomic():
        user = await uow.users.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
        
    return UserResponse(**user)

def require_roles(required_roles: list[str]):
    async def role_checker(
        user: Annotated[UserResponse, Depends(get_current_user)]
    ) -> UserResponse:
        if user.role not in required_roles:
            raise InsufficientPermissionsError()
        return user
    return role_checker

get_current_employee = require_roles(["employee"])
get_current_moderator = require_roles(["moderator"])
get_current_staff = require_roles(["employee", "moderator"])