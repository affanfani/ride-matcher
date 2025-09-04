from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")
    full_name: str = Field(..., min_length=2, description="User full name")
    user_type: Literal["rider", "driver"] = Field(..., description="User type: rider or driver")

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserOut(BaseModel):
    """Schema for user output"""
    id: str
    email: str
    full_name: str
    user_type: Literal["rider", "driver"]
    
    class Config:
        from_attributes = True
