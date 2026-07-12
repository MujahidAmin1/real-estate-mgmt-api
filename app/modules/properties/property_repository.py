from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.properties.property_filters import PropertyFilters
from app.modules.properties.property_models import Favorite, Property, PropertyImage


class PropertyRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, property_id: uuid.UUID) -> Optional[Property]:
        return self.db.query(Property).filter(Property.id == property_id).first()

    def create(self, property: Property) -> Property:
        self.db.add(property)
        self.db.flush()
        return property

    def save(self, property: Property) -> Property:
        self.db.commit()
        self.db.refresh(property)
        return property

    def delete(self, property: Property) -> None:
        self.db.delete(property)
        self.db.commit()

    def find_all(
        self, filters: PropertyFilters, offset: int, limit: int
    ) -> tuple[list[Property], int]:
        query = self.db.query(Property)

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
            query.order_by(Property.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return properties, total

    def find_by_agent(
        self, agent_id: uuid.UUID, status: Optional[str], offset: int, limit: int
    ) -> tuple[list[Property], int]:
        query = self.db.query(Property).filter(Property.agent_id == agent_id)

        if status:
            query = query.filter(Property.status == status)

        total = query.count()
        properties = (
            query.order_by(Property.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return properties, total


class PropertyImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_all(self, images: list[PropertyImage]) -> None:
        self.db.add_all(images)
        self.db.flush()


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_user_and_property(
        self, user_id: uuid.UUID, property_id: uuid.UUID
    ) -> Optional[Favorite]:
        return self.db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.property_id == property_id,
        ).first()

    def create(self, favorite: Favorite) -> Favorite:
        self.db.add(favorite)
        self.db.commit()
        return favorite

    def delete(self, favorite: Favorite) -> None:
        self.db.delete(favorite)
        self.db.commit()
