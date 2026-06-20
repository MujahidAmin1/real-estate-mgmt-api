from datetime import datetime
from decimal import Decimal
import enum, uuid
from typing import Optional
from sqlalchemy import DECIMAL, UUID, DateTime, Enum, ForeignKey, String, Text, func

from app.db.database import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    reference: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Paystack reference
    amount: Mapped[Decimal] = mapped_column(DECIMAL(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, server_default="NGN")
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), nullable=False, server_default=PaymentStatus.pending.value)
    paystack_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # raw JSON from Paystack, useful for debugging
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())