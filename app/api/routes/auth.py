from fastapi import APIRouter, Depends
from app.db.models import User
from app.schemas.auth import UserCreate, UserLogin, UserOut, Token
from app.services.auth import AuthService, get_auth_service
from app.utils.auth import get_current_user

router = APIRouter(tags=["authentication"])

@router.post("/register", response_model=UserOut, status_code=201)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user (rider or driver)"""
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=Token)
async def login_user(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return access token"""
    return await auth_service.login_user(credentials)

@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user
