from api.deps import get_auth_service
from fastapi import APIRouter, Depends, status
from schemas.auth import AuthResponse, DummyLoginRequest, LoginRequest, RegisterRequest
from services.auth import AuthService

router = APIRouter()


@router.post("/dummyLogin", response_model=AuthResponse)
async def dummy_login(request: DummyLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    token = await auth_service.dummy_login(request.role)
    return {"token": token}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.register_user(request.email, request.password, request.role)
    return {"id": user["id"], "email": user["email"], "role": user["role"]}


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    token = await auth_service.login_user(request.email, request.password)
    return {"token": token}
