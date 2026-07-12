from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.pagination_schema import PaginatedResponse, PaginationMeta
from app.modules.properties.property_exceptions import (
    CloudinaryOperationError,
    FavoriteAlreadyExists,
    FavoriteNotFound,
    ImageUploadError,
    InvalidImageError,
    PropertyNotFound,
)
from app.modules.properties.property_filters import PropertyFilters
from app.modules.properties.property_models import Favorite, Property, PropertyImage
from app.modules.properties.property_repository import (
    FavoriteRepository,
    PropertyImageRepository,
    PropertyRepository,
)
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User
from app.services.cloudinary import (
    CloudinaryUploadError,
    InvalidImageFileError,
    delete_image,
    upload_images,
)
from app.utils.exceptions import ForbiddenException


class PropertyService:
    def __init__(self, db: Session):
        self.db = db
        self.property_repo = PropertyRepository(db)
        self.image_repo = PropertyImageRepository(db)
        self.favorite_repo = FavoriteRepository(db)

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
            raise InvalidImageError(str(exc)) from exc
        except CloudinaryUploadError as exc:
            raise CloudinaryOperationError(str(exc)) from exc

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
            self.property_repo.create(property)

            images_models = [
                PropertyImage(
                    property_id=property.id,
                    image_url=img.image_url,
                    public_id=img.public_id,
                    is_primary=index == 0,
                )
                for index, img in enumerate(uploaded_images)
            ]
            self.image_repo.create_all(images_models)

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
        property = self.property_repo.find_by_id(property_id)
        if not property:
            raise PropertyNotFound()

        if property.agent_id != current_user.id and current_user.role != UserRole.admin:
            raise ForbiddenException()

        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(property, key, value)

        return self.property_repo.save(property)

    def delete_property(self, property_id: uuid.UUID, current_user: User) -> None:
        property = self.property_repo.find_by_id(property_id)
        if not property:
            raise PropertyNotFound()

        if property.agent_id != current_user.id and current_user.role != UserRole.admin:
            raise ForbiddenException()

        for image in property.images:
            delete_image(image.public_id)

        self.property_repo.delete(property)

    def get_properties(
        self, filters: PropertyFilters, page: int, limit: int
    ) -> PaginatedResponse:
        offset = (page - 1) * limit
        properties, total = self.property_repo.find_all(filters, offset, limit)
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
        property = self.property_repo.find_by_id(property_id)
        if not property:
            raise PropertyNotFound()
        return property

    def get_agent_listings(
        self,
        agent_id: uuid.UUID,
        status: Optional[str],
        page: int,
        limit: int,
    ) -> PaginatedResponse:
        offset = (page - 1) * limit
        properties, total = self.property_repo.find_by_agent(
            agent_id, status, offset, limit
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
        property = self.property_repo.find_by_id(property_id)
        if not property:
            raise PropertyNotFound()

        existing = self.favorite_repo.find_by_user_and_property(
            current_user.id, property_id
        )
        if existing:
            raise FavoriteAlreadyExists()

        favorite = Favorite(user_id=current_user.id, property_id=property_id)
        self.favorite_repo.create(favorite)
        return {"message": "Property favorited successfully"}

    def remove_favorite(self, property_id: uuid.UUID, current_user: User) -> None:
        favorite = self.favorite_repo.find_by_user_and_property(
            current_user.id, property_id
        )
        if not favorite:
            raise FavoriteNotFound()
        self.favorite_repo.delete(favorite)
