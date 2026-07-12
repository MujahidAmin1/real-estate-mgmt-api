from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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
