from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.properties.property import Property

class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid7
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False
    )

    image_url: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    property: Mapped[Property] = relationship(
        "Property",
        back_populates="images"
    )