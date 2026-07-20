# schemas/conversation.py
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, ConfigDict


class SendMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_one_id: uuid.UUID
    user_two_id: uuid.UUID
    property_id: uuid.UUID
    last_message_text: str | None
    last_message_at: datetime | None
    unread_count: int  # already resolved for the requesting user
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
