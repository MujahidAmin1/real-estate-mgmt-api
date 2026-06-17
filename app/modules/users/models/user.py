from datetime import datetime

from sqlalchemy import UUID, Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
import uuid
from app.db.database import Base
from app.modules.properties.models.property import Property
from app.modules.users.models.agent_profile import AgentProfile
from app.modules.users.user_enums import OnboardingStatus, UserRole
from app.modules.users.models.user_profile import UserProfile

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid7
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.client
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus),
        nullable=False,
        default=OnboardingStatus.not_started
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    agent_profile: Mapped["AgentProfile"] = relationship("AgentProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    user_profile: Mapped["UserProfile"] = relationship("UserProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    properties: Mapped[list["Property"]] = relationship("Property", backref="agent", cascade="all, delete-orphan")