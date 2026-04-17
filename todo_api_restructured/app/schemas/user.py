from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from app.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    role: UserRole
    is_email_verified: bool
    receive_notifications: bool
    created_at: datetime


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
