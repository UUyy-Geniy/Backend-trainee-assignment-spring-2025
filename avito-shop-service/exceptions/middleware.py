from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .app_exception import AppException, ErrorType

error_type_to_status_code = {
    ErrorType.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorType.VALIDATION: status.HTTP_400_BAD_REQUEST,
    ErrorType.BUSINESS: status.HTTP_400_BAD_REQUEST,
    ErrorType.AUTH: status.HTTP_401_UNAUTHORIZED,
    ErrorType.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: callable):
        try:
            response = await call_next(request)
            return response
        except AppException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "type": exc.error_type,
                        "message": exc.message,
                        "details": exc.details
                    }
                }
            )
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "type": ErrorType.SYSTEM,
                        "message": "Internal server error",
                        "details": {"exception": str(exc)}
                    }
                }
            )
