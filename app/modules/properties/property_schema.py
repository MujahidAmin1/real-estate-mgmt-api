from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.properties.property_enum import ListingType, PropertyStatus, PropertyType


class PropertyImageResponse(BaseModel):
    id: UUID
    property_id: UUID
    image_url: str
    public_id: str
    is_primary: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PropertyCreate(BaseModel):
    title: str
    description: str
    price: Decimal
    currency: str = "NGN"
    property_type: PropertyType
    listing_type: ListingType
    status: PropertyStatus = PropertyStatus.available
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_sqm: Optional[float] = None
    location_text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: list[PropertyImageCreate]

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class PropertyImageCreate(BaseModel):
    image_url: str
    public_id: str
    is_primary: bool = False


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    property_type: Optional[PropertyType] = None
    listing_type: Optional[ListingType] = None
    status: Optional[PropertyStatus] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_sqm: Optional[float] = None
    location_text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyResponse(BaseModel):
    id: UUID
    agent_id: UUID
    title: str
    description: str
    price: Decimal
    currency: str
    property_type: PropertyType
    listing_type: ListingType
    status: PropertyStatus
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    size_sqm: Optional[float] = None
    location_text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    images: list[PropertyImageResponse] = []

    model_config = ConfigDict(from_attributes=True)
