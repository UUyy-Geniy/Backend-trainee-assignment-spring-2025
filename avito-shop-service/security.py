from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import status

from core.config import settings
from exceptions.app_exception import AppException, ErrorType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            raise JWTError("Missing expiration in token")
        if datetime.fromtimestamp(exp_timestamp) < datetime.now():
            raise JWTError("Token expired")
        return payload
    except JWTError as exc:
        raise JWTError("Invalid token") from exc