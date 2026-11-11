from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole, UserStatus

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    password: str = Field(..., min_length=8, max_length=72)
    full_name: Optional[str] = None
    user_type: Optional[str] = "individual"
    institution_type: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=72)

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    user_type: Optional[str] = "individual"
    institution_type: Optional[str] = None
    role: UserRole
    status: UserStatus
    created_at: datetime
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    full_name: Optional[str] = None
    institution_type: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class MessageResponse(BaseModel):
    message: str
    success: bool = True
