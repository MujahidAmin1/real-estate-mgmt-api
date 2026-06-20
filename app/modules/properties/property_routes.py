from __future__ import annotations
from decimal import Decimal
import os
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.services.cloudinary import delete_image, upload_image
from app.db.database import get_db
from app.modules.properties.property_enum import ListingType, PropertyStatus, PropertyType
from app.modules.properties.property_filters import PropertyFilters
from app.modules.users.user_enums import UserRole
from app.modules.properties.models.property import Property
from app.modules.properties.models.property_image import PropertyImage
from app.modules.users.models.user import User
from app.modules.properties.property_schema import PropertyResponse, PropertyUpdate
from app.utils.dependencies import require_role
import asyncio
from functools import partial
from app.utils.exceptions import NotFoundException, ForbiddenException
router = APIRouter(prefix="/properties", tags=["Properties"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "properties")

@router.post("/", status_code=201, response_model=PropertyResponse)
async def create_property(
    title: str = Form(...),
    description: str = Form(...),
    price: Decimal = Form(...),
    location_text: str = Form(...),
    property_type: PropertyType = Form(...),
    listing_type: ListingType = Form(...),
    currency: str = Form("NGN"),
    status: PropertyStatus = Form(PropertyStatus.available),
    bedrooms: Optional[int] = Form(None),
    bathrooms: Optional[int] = Form(None),
    size_sqm: Optional[float] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    images: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent, UserRole.admin)),
):
    if not images:
        raise HTTPException(status_code=422, detail="At least one image is required")

    loop = asyncio.get_event_loop()
    contents = await asyncio.gather(*[img.read() for img in images])
    upload_results = await asyncio.gather(*[
        loop.run_in_executor(None, partial(upload_image, content, "properties"))
        for content in contents
    ])

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
        image_urls=",".join(r["url"] for r in upload_results),
    )
    db.add(property)
    db.flush()

    db.add_all([
        PropertyImage(
            property_id=property.id,
            image_url=result["url"],
            public_id=result["public_id"],
            is_primary=(idx == 0),
            sort_order=idx,
        )
        for idx, result in enumerate(upload_results)
    ])

    db.commit()
    db.refresh(property)
    return property

@router.put("/{property_id}", response_model=PropertyResponse)
def update_post(
    property_id: uuid.UUID,
    body: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.agent))
):
    
    property = db.query(Property).filter(Property.id == property_id).first()

    if not property:
        raise NotFoundException("Post not found")

    if property.agent_id != current_user.id and current_user.role != UserRole.agent:
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
    
    
@router.get("/", response_model=PropertyResponse)
def get_properties(
    filters: PropertyFilters = Depends(),
    db: Session = Depends(get_db),
    ):
    query = db.query(Property)
    if filters.property_type:
        query.filter(Property.property_type == filters.property_type)
        
    if filters.listing_type:
        query = query.filter(Property.listing_type == filters.listing_type)

    if filters.property_status:
        query = query.filter(Property.status == filters.property_status)

    if filters.min_price is not None:
        query = query.filter(Property.price >= filters.min_price)

    if filters.max_price is not None:
        query = query.filter(Property.price <= filters.max_price)

    return query.all()
