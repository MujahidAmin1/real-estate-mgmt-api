from __future__ import annotations

from datetime import datetime 
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
import uuid
from app.db.database import Base
from sqlalchemy import DECIMAL, UUID, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.modules.properties.property_enum import ListingType, PropertyStatus, PropertyType

if TYPE_CHECKING:
    from app.modules.properties.models.property_image import PropertyImage

class Property(Base):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid7
    )

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(String, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    price: Mapped[Decimal] = mapped_column(DECIMAL(14, 2), nullable=False)

    currency: Mapped[str] = mapped_column(String, nullable=False, server_default="NGN")

    property_type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType),
        nullable=False
    )

    listing_type: Mapped[ListingType] = mapped_column(
        Enum(ListingType),
        nullable=False
    )

    status: Mapped[PropertyStatus] = mapped_column(
        Enum(PropertyStatus),
        nullable=False,
        server_default=PropertyStatus.available.value
    )
    
    image_urls: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    bathrooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    size_sqm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    location_text: Mapped[str] = mapped_column(String, nullable=False)

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    images: Mapped[list[PropertyImage]] = relationship(
        "PropertyImage",
        back_populates="property",
        cascade="all, delete-orphan"
    )