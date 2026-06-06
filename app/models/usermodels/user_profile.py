from sqlalchemy import UUID, ForeignKey, String, Text
from sqlalchemy.orm import mapped_column, Mapped
from typing import Optional
import uuid
from app.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(String, nullable=False)

    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    profile_image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)