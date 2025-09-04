from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import get_session
from app.db.models import User, UserType

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if user_id is None:
            raise credentials_exception
            
        return {"user_id": user_id, "user_type": user_type}
        
    except JWTError:
        raise credentials_exception

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    stmt = select(User).where(User.id == token_data["user_id"], User.is_active == True)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user

async def get_current_rider(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they are a rider"""
    if current_user.user_type != UserType.RIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only riders can perform this action"
        )
    return current_user

async def get_current_driver(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they are a driver"""
    if current_user.user_type != UserType.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can perform this action"
        )
    return current_user

async def authenticate_user(email: str, password: str, session: AsyncSession) -> Optional[User]:
    """Authenticate user by email and password"""
    stmt = select(User).where(User.email == email, User.is_active == True)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
