from app.database import Base

from sqlalchemy import UUID, Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
import uuid
from app.database import Base
from app.models.enums import OnboardingStatus, UserRole

class AgentProfile(Base):
    __tablename__ = "agent_profiles"

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

    agency_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    experience_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)