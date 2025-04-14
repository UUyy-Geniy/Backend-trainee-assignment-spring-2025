import logging
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    NOT_FOUND = "not_found"
    VALIDATION = "validation_error"
    BUSINESS = "business_rule_violation"
    AUTH = "authentication_error"
    SYSTEM = "system_error"


class AppException(Exception):
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.error_type = error_type
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        logger.error(f"{error_type}: {message}", extra=details)


class UserAlreadyExistsError(AppException):
    def __init__(self, email: str):
        super().__init__(
            error_type=ErrorType.BUSINESS,
            message="Email already registered",
            status_code=400,
            details={"email": email},
        )


class UserNotFoundError(AppException):
    def __init__(self, message: str = "User not found"):
        super().__init__(
            error_type=ErrorType.NOT_FOUND,
            message=message,
            status_code=404,
        )


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(error_type=ErrorType.AUTH, message="Invalid credentials", status_code=401)


class ActiveReceptionExistsError(AppException):
    def __init__(self):
        super().__init__(
            error_type=ErrorType.BUSINESS,
            message="Active reception already exists",
            status_code=400,
        )


class NoActiveReceptionError(AppException):
    def __init__(self):
        super().__init__(
            error_type=ErrorType.BUSINESS,
            message="No active reception",
            status_code=400,
        )


class InsufficientPermissionsError(AppException):
    def __init__(self):
        super().__init__(
            error_type=ErrorType.BUSINESS,
            message="Insufficient permissions",
            status_code=403,
        )


class NoProductToDeleteError(AppException):
    def __init__(self):
        super().__init__(
            error_type=ErrorType.BUSINESS,
            message="No product to delete",
            status_code=400,
        )


class PVZNotFoundError(AppException):
    def __init__(self):
        super().__init__(
            error_type=ErrorType.NOT_FOUND,
            message="PVZ not found",
            status_code=404,
        )
