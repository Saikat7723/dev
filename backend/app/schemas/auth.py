from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

TokenResponse.model_rebuild()
