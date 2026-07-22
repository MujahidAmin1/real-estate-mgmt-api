# schemas/payment.py
import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PaymentInitializeRequest(BaseModel):
    property_id: uuid.UUID


class PaymentInitializeResponse(BaseModel):
    access_code: str
    reference: str


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2, was orm_mode in v1

    id: uuid.UUID
    property_id: uuid.UUID
    reference: str
    amount: Decimal
    currency: str
    status: str  # or PaymentStatus if you import the enum here
    created_at: datetime