from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.pagination_schema import PaginatedResponse, PaginationMeta
from app.db.database import get_db
from app.modules.properties.property_enums import ListingType, PropertyStatus, PropertyType
from app.modules.properties.property_exceptions import (
    CloudinaryOperationError,
    FavoriteAlreadyExists,
    FavoriteNotFound,
    InvalidImageError,
    PropertyNotFound,
)
from app.modules.properties.property_filters import PropertyFilters
from app.modules.properties.property_schemas import PropertyResponse, PropertyUpdate
from app.modules.properties.property_service import PropertyService
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User
from app.utils.dependencies import PaginationParams, require_role
from app.utils.exceptions import ForbiddenException

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/", status_code=201, response_model=PropertyResponse)
def create_property(
    title: Annotated[str, Form(...)],
    description: Annotated[str, Form(...)],
    price: Annotated[Decimal, Form(...)],
    location_text: Annotated[str, Form(...)],
    property_type: Annotated[PropertyType, Form(...)],
    listing_type: Annotated[ListingType, Form(...)],
    images: Annotated[list[UploadFile], File(...)],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
    currency: Annotated[str, Form()] = "NGN",
    status: Annotated[PropertyStatus, Form()] = PropertyStatus.available,
    bedrooms: Annotated[Optional[int], Form()] = None,
    bathrooms: Annotated[Optional[int], Form()] = None,
    size_sqm: Annotated[Optional[float], Form()] = None,
    latitude: Annotated[Optional[float], Form()] = None,
    longitude: Annotated[Optional[float], Form()] = None,
):
    if price <= 0:
        raise HTTPException(status_code=422, detail="Price must be greater than 0")

    service = PropertyService(db)
    try:
        return service.create_property(
            current_user=current_user,
            title=title,
            description=description,
            price=price,
            location_text=location_text,
            property_type=property_type,
            listing_type=listing_type,
            images=images,
            currency=currency,
            status=status,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            size_sqm=size_sqm,
            latitude=latitude,
            longitude=longitude,
        )
    except InvalidImageError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CloudinaryOperationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: uuid.UUID,
    body: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent)),
):
    service = PropertyService(db)
    try:
        return service.update_property(property_id, body, current_user)
    except PropertyNotFound:
        raise HTTPException(status_code=404, detail="Property not found")
    except ForbiddenException as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.delete("/{property_id}", status_code=204)
def delete_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
):
    service = PropertyService(db)
    try:
        service.delete_property(property_id, current_user)
    except PropertyNotFound:
        raise HTTPException(status_code=404, detail="Property not found")
    except ForbiddenException as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.get("/", response_model=PaginatedResponse[PropertyResponse])
def get_properties(
    pagination: PaginationParams = Depends(),
    filters: PropertyFilters = Depends(),
    db: Session = Depends(get_db),
):
    service = PropertyService(db)
    return service.get_properties(filters, pagination.page, pagination.limit)


@router.get("/{property_id}")
def get_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = PropertyService(db)
    try:
        return service.get_property(property_id)
    except PropertyNotFound:
        raise HTTPException(status_code=404, detail="Property not found")


@router.get("/agent/{agent_id}", response_model=PaginatedResponse[PropertyResponse])
def get_agent_listings(
    agent_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
    filters: PropertyFilters = Depends(),
    pagination: PaginationParams = Depends(),
):
    service = PropertyService(db)
    return service.get_agent_listings(
        agent_id, filters.property_status, pagination.page, pagination.limit
    )


@router.post("/{property_id}/favorite", status_code=201)
def favourite_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.client)),
):
    service = PropertyService(db)
    try:
        return service.add_favorite(property_id, current_user)
    except PropertyNotFound:
        raise HTTPException(status_code=404, detail="Property not found")
    except FavoriteAlreadyExists as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.delete("/{property_id}/favorite", status_code=204)
def unfavourite_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.client)),
):
    service = PropertyService(db)
    try:
        service.remove_favorite(property_id, current_user)
    except FavoriteNotFound:
        raise HTTPException(status_code=404, detail="Favorite not found")
