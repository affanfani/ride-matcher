from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import get_settings

settings = get_settings()
security = HTTPBearer()

class AuthMiddleware:
    """Middleware for user authentication and API validation"""
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            user_type: str = payload.get("user_type")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            return {"user_id": user_id, "user_type": user_type}
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    
    @staticmethod
    def validate_rider(user_data: dict):
        """Validate that user is a rider"""
        if user_data.get("user_type") != "rider":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only riders can perform this action"
            )
    
    @staticmethod
    def validate_driver(user_data: dict):
        """Validate that user is a driver"""
        if user_data.get("user_type") != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can perform this action"
            )
    
    @staticmethod
    async def validate_api_request(request: Request):
        """General API request validation"""
        # Add any general API validation logic here
        if request.method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Method not allowed"
            )
