from typing import Annotated, AsyncGenerator
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncConnection
from contextlib import asynccontextmanager

from core.config import settings
from core.engine import get_connection

from schemas.user import UserResponse
from repository.unit_of_work import UnitOfWork
from services.user import UserService
from services.auth import AuthService
from exceptions.app_exception import InvalidCredentialsError, UserNotFoundError
        
async def get_uow(conn: AsyncConnection = Depends(get_connection)) -> UnitOfWork:
    try:
        yield UnitOfWork(conn)
    finally:
        await conn.close()



def get_user_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> UserService:
    return UserService(uow)

def get_auth_service(
    uow: Annotated[UnitOfWork, Depends(get_uow)]
) -> AuthService:
    return AuthService(uow)


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

    user = await uow.users.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
        
    return UserResponse(**user)

def require_role(role: str):
    async def role_checker(
        user: Annotated[dict, Depends(get_current_user)]
    ) -> dict:
        if user["role"] != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return role_checker

get_current_employee = require_role("employee")
get_current_moderator = require_role("moderator")
