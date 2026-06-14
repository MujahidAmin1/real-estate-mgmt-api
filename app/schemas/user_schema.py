from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator

from app.enums.user_enums import OnboardingStatus, UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.client

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool
    onboarding_status: OnboardingStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoginDto(BaseModel):
    email: EmailStr
    password: str
    
class RefreshSchema(BaseModel):
    refresh_token: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    onboarding_status: Optional[OnboardingStatus] = None


class UserProfileCreate(BaseModel):
    full_name: str
    phone_number: Optional[str] = None
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    phone_number: Optional[str] = None
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None


class AgentProfileCreate(BaseModel):
    agency_name: Optional[str] = None
    experience_years: Optional[int] = None
    is_verified: bool = False


class AgentProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    agency_name: Optional[str] = None
    experience_years: Optional[int] = None
    is_verified: bool

    model_config = {"from_attributes": True}


class AgentProfileUpdate(BaseModel):
    agency_name: Optional[str] = None
    experience_years: Optional[int] = None
    is_verified: Optional[bool] = None
