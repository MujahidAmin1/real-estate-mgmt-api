from datetime import datetime

from sqlalchemy import UUID, Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
import uuid
from app.database import Base
from app.models.agent_profile import AgentProfile
from app.models.enums import OnboardingStatus, UserRole

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
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
    default=OnboardingStatus.not_started)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    agent_profile: Mapped["AgentProfile"] = relationship("AgentProfile", backref="user", uselist=False, cascade="all, delete-orphan")