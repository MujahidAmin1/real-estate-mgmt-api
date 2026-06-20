
from datetime import datetime
import uuid
from sqlalchemy import UUID, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.db.database import Base
from app.modules.properties.models.property import Property
from app.modules.users.models.user import User

class Favorite(Base):
    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "property_id",
            name="uq_user_property_favorite"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
    "User",
    back_populates="favorites"
    )

    property = relationship(
        "Property",
        back_populates="favorites"
    )