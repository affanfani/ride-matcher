from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from datetime import timedelta
import uuid
import logging

from app.db.models import User, UserType
from app.schemas.auth import UserCreate, UserLogin, UserOut, Token
from app.utils.auth import get_password_hash, authenticate_user, create_access_token
from app.core.config import get_settings
from app.db.session import get_session

logger = logging.getLogger(__name__)
settings = get_settings()

class AuthService:
    """Service class for authentication operations with dependency injection"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, user_data: UserCreate) -> UserOut:
        """Register a new user (rider or driver)"""
        try:
            # Check if user already exists
            stmt = select(User).where(User.email == user_data.email)
            result = await self.session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            user = User(
                id=str(uuid.uuid4()),
                email=user_data.email,
                hashed_password=get_password_hash(user_data.password),
                full_name=user_data.full_name,
                user_type=UserType(user_data.user_type),
                is_active=True
            )
            
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            
            logger.info(f"New user registered: {user.email} as {user.user_type.value}")
            return user
            
        except HTTPException:
            await self.session.rollback()
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to register user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )

    async def login_user(self, credentials: UserLogin) -> Token:
        """Authenticate user and return access token"""
        try:
            user = await authenticate_user(credentials.email, credentials.password, self.session)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={
                    "sub": user.id,
                    "user_type": user.user_type.value
                },
                expires_delta=access_token_expires
            )
            
            logger.info(f"User logged in: {user.email}")
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to login user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to login"
            )

# Dependency injection function
def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """Dependency injection for AuthService"""
    return AuthService(session)
