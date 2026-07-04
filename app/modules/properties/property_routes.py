from __future__ import annotations
from decimal import Decimal
from typing import Annotated, Optional
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.pagination_schema import PaginatedResponse, PaginationMeta
from app.services.cloudinary import (
    CloudinaryUploadError,
    InvalidImageFileError,
    delete_image,
    upload_images,
)
from app.db.database import get_db
from app.modules.properties.property_enum import ListingType, PropertyStatus, PropertyType
from app.modules.properties.property_filters import PropertyFilters
from app.modules.users.user_enums import UserRole
from app.modules.properties.models.property import Property
from app.modules.properties.models.property_image import PropertyImage
from app.modules.users.models.user import User
from app.modules.properties.property_schema import (
    PropertyResponse,
    PropertyUpdate,
)
from app.utils.dependencies import PaginationParams, require_role
from app.utils.exceptions import NotFoundException, ForbiddenException

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

    try:
        uploaded_images = upload_images(images, folder="properties")
    except InvalidImageFileError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except CloudinaryUploadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        property = Property(
            agent_id=current_user.id,
            title=title,
            description=description,
            price=price,
            currency=currency,
            property_type=property_type,
            listing_type=listing_type,
            status=status,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            size_sqm=size_sqm,
            location_text=location_text,
            latitude=latitude,
            longitude=longitude,
        )
        db.add(property)
        db.flush()

        db.add_all(
            [
                PropertyImage(
                    property_id=property.id,
                    image_url=img.image_url,
                    public_id=img.public_id,
                    is_primary=index == 0,
                )
                for index, img in enumerate(uploaded_images)
            ]
        )

        db.commit()
        db.refresh(property)
    except Exception:
        db.rollback()
        for image in uploaded_images:
            delete_image(image.public_id)
        raise

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


@router.get("/agent/{agent_id}", response_model=PaginatedResponse[PropertyResponse])
def get_agent_listings(
    agent_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
    filters: PropertyFilters = Depends(),
    pagination: PaginationParams = Depends(),
):
    query = db.query(Property).filter(Property.agent_id == agent_id)

    if filters.property_status:
        query = query.filter(Property.status == filters.property_status)

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
    