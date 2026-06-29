from __future__ import annotations

from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.pagination_schema import PaginatedResponse, PaginationMeta
from app.services.cloudinary import delete_image
from app.db.database import get_db
from app.modules.properties.property_enum import ListingType, PropertyStatus, PropertyType
from app.modules.properties.property_filters import PropertyFilters
from app.modules.users.user_enums import UserRole
from app.modules.properties.models.property import Property
from app.modules.properties.models.property_image import PropertyImage
from app.modules.users.models.user import User
from app.modules.properties.property_schema import (
    PropertyCreate,
    PropertyResponse,
    PropertyUpdate,
)
from app.utils.dependencies import PaginationParams, require_role
from app.utils.exceptions import NotFoundException, ForbiddenException

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/", status_code=201, response_model=PropertyResponse)
def create_property(
    body: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
):
    if not body.images:
        raise HTTPException(status_code=422, detail="At least one image is required")

    property = Property(
        agent_id=current_user.id,
        title=body.title,
        description=body.description,
        price=body.price,
        currency=body.currency,
        property_type=body.property_type,
        listing_type=body.listing_type,
        status=body.status,
        bedrooms=body.bedrooms,
        bathrooms=body.bathrooms,
        size_sqm=body.size_sqm,
        location_text=body.location_text,
        latitude=body.latitude,
        longitude=body.longitude,
    )
    db.add(property)
    db.flush()

    db.add_all(
        [
            PropertyImage(
                property_id=property.id,
                image_url=img.image_url,
                public_id=img.public_id,
                is_primary=img.is_primary,
                sort_order=img.sort_order,
            )
            for img in body.images
        ]
    )

    property.image_urls = ",".join(img.image_url for img in body.images)

    db.commit()
    db.refresh(property)
    return property


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: uuid.UUID,
    body: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent)),
):
    property = db.query(Property).filter(Property.id == property_id).first()

    if not property:
        raise NotFoundException("Property not found")

    if property.agent_id != current_user.id and current_user.role != UserRole.admin:
        raise ForbiddenException()

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(property, key, value)

    db.commit()
    db.refresh(property)
    return property


@router.delete("/{property_id}", status_code=204)
def delete_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
):
    property = db.query(Property).filter(Property.id == property_id).first()

    if not property:
        raise NotFoundException("Property not found")

    if property.agent_id != current_user.id and current_user.role != UserRole.admin:
        raise ForbiddenException()

    for image in property.images:
        delete_image(image.public_id)

    db.delete(property)
    db.commit()


@router.get("/", response_model=PaginatedResponse[PropertyResponse])
def get_properties(
    pagination: PaginationParams = Depends(),
    filters: PropertyFilters = Depends(),
    db: Session = Depends(get_db),
):
    query = db.query(Property)

    if filters.property_type:
        query = query.filter(Property.property_type == filters.property_type)

    if filters.listing_type:
        query = query.filter(Property.listing_type == filters.listing_type)

    if filters.property_status:
        query = query.filter(Property.status == filters.property_status)

    if filters.min_price is not None:
        query = query.filter(Property.price >= filters.min_price)

    if filters.max_price is not None:
        query = query.filter(Property.price <= filters.max_price)

    total = query.count()

    properties = (
        query
        .order_by(Property.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
        .all()
    )

    return PaginatedResponse(
        data=properties,
        meta=PaginationMeta(
            total=total,
            page=pagination.page,
            limit=pagination.limit,
            pages=-(-total // pagination.limit),
        ),
    )


@router.get("/{property_id}")
def get_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    property = db.query(Property).filter(Property.id == property_id).first()

    if not property:
        raise NotFoundException("Property not found")

    return property


@router.get("/agent/{agent_id}")
def get_agent_listings(
    agent_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
    filters: PropertyFilters = Depends(),
):
    query = db.query(Property).filter(Property.agent_id == agent_id)

    if filters.property_status:
        query = query.filter(Property.status == filters.property_status)

    return query.all()
