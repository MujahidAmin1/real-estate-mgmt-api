from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.pagination_schema import PaginatedResponse, PaginationMeta
from app.modules.properties.property_models import Favorite, Property, PropertyImage
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User
from app.services.cloudinary import (
    CloudinaryUploadError,
    InvalidImageFileError,
    delete_image,
    upload_images,
)
from app.utils.exceptions import AppError


class PropertyService:
    def __init__(self, db: Session):
        self.db = db

    def create_property(
        self,
        current_user: User,
        title: str,
        description: str,
        price: Decimal,
        location_text: str,
        property_type: str,
        listing_type: str,
        images: list[UploadFile],
        currency: str = "NGN",
        status: str = "available",
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        size_sqm: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Property:
        try:
            uploaded_images = upload_images(images, folder="properties")
        except InvalidImageFileError as exc:
            raise AppError(422, str(exc)) from exc
        except CloudinaryUploadError as exc:
            raise AppError(502, str(exc)) from exc

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
            self.db.add(property)
            self.db.flush()

            for index, img in enumerate(uploaded_images):
                self.db.add(
                    PropertyImage(
                        property_id=property.id,
                        image_url=img.image_url,
                        public_id=img.public_id,
                        is_primary=index == 0,
                    )
                )

            self.db.commit()
            self.db.refresh(property)
        except Exception:
            self.db.rollback()
            for image in uploaded_images:
                delete_image(image.public_id)
            raise

        return property

    def update_property(
        self, property_id: uuid.UUID, body, current_user: User
    ) -> Property:
        property = self.db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise AppError(404, "Property not found")

        if property.agent_id != current_user.id and current_user.role != UserRole.admin:
            raise AppError(403, "Insufficient permissions")

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(property, key, value)

        self.db.commit()
        self.db.refresh(property)
        return property

    def delete_property(self, property_id: uuid.UUID, current_user: User) -> None:
        property = self.db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise AppError(404, "Property not found")

        if property.agent_id != current_user.id and current_user.role != UserRole.admin:
            raise AppError(403, "Insufficient permissions")

        for image in property.images:
            delete_image(image.public_id)

        self.db.delete(property)
        self.db.commit()

    def get_properties(
        self, property_type, listing_type, property_status, min_price, max_price, page: int, limit: int
    ) -> PaginatedResponse:
        query = self.db.query(Property)

        if property_type:
            query = query.filter(Property.property_type == property_type)
        if listing_type:
            query = query.filter(Property.listing_type == listing_type)
        if property_status:
            query = query.filter(Property.status == property_status)
        if min_price is not None:
            query = query.filter(Property.price >= min_price)
        if max_price is not None:
            query = query.filter(Property.price <= max_price)

        total = query.count()
        offset = (page - 1) * limit
        properties = (
            query.order_by(Property.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return PaginatedResponse(
            data=properties,
            meta=PaginationMeta(
                total=total,
                page=page,
                limit=limit,
                pages=-(-total // limit),
            ),
        )

    def get_property(self, property_id: uuid.UUID) -> Property:
        property = self.db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise AppError(404, "Property not found")
        return property

    def get_agent_listings(
        self,
        agent_id: uuid.UUID,
        status: Optional[str],
        page: int,
        limit: int,
    ) -> PaginatedResponse:
        query = self.db.query(Property).filter(Property.agent_id == agent_id)

        if status:
            query = query.filter(Property.status == status)

        total = query.count()
        offset = (page - 1) * limit
        properties = (
            query.order_by(Property.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return PaginatedResponse(
            data=properties,
            meta=PaginationMeta(
                total=total,
                page=page,
                limit=limit,
                pages=-(-total // limit),
            ),
        )

    def add_favorite(self, property_id: uuid.UUID, current_user: User) -> dict:
        property = self.db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise AppError(404, "Property not found")

        existing = self.db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.property_id == property_id,
        ).first()
        if existing:
            raise AppError(409, "Property is already favorited")

        self.db.add(Favorite(user_id=current_user.id, property_id=property_id))
        self.db.commit()
        return {"message": "Property favorited successfully"}

    def remove_favorite(self, property_id: uuid.UUID, current_user: User) -> None:
        favorite = self.db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.property_id == property_id,
        ).first()
        if not favorite:
            raise AppError(404, "Favorite not found")

        self.db.delete(favorite)
        self.db.commit()
