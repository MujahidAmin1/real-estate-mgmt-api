import uuid
from typing import Optional

from app.db.database import Base
from sqlalchemy import UUID, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, Mapped


class AgentProfile(Base):
    __tablename__ = "agent_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid7
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
