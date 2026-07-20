import uuid
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.dependencies import get_current_user
from app.modules.users.auth_models import User

from app.modules.conversation.conversation_schemas import ConversationResponse, MessageResponse, SendMessageRequest
from app.modules.conversation.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("/{property_id}", response_model=ConversationResponse, status_code=201)
def start_conversation(
    property_id: uuid.UUID,
    agent_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ConversationService(db)
    conversation = service.get_or_create_conversation(
        property_id=property_id,
        user_a=current_user.id,
        user_b=agent_id,
    )
    return ConversationResponse(
        id=conversation.id,
        user_one_id=conversation.user_one_id,
        user_two_id=conversation.user_two_id,
        property_id=conversation.property_id,
        last_message_text=conversation.last_message_text,
        last_message_at=conversation.last_message_at,
        unread_count=service.resolve_unread_count(conversation, current_user.id),
        created_at=conversation.created_at,
    )


@router.get("/", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ConversationService(db)
    return [
        ConversationResponse(
            id=c.id,
            user_one_id=c.user_one_id,
            user_two_id=c.user_two_id,
            property_id=c.property_id,
            last_message_text=c.last_message_text,
            last_message_at=c.last_message_at,
            unread_count=service.resolve_unread_count(c, current_user.id),
            created_at=c.created_at,
        )
        for c in service.get_user_conversations(current_user.id)
    ]


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def get_messages(
    conversation_id: uuid.UUID,
    before: datetime | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ConversationService(db)
    return service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=min(limit, 100),
        before=before,
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=201)
def send_message(
    conversation_id: uuid.UUID,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ConversationService(db)
    return service.send_message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=body.content,
    )


@router.patch("/{conversation_id}/read", status_code=204)
def mark_read(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ConversationService(db)
    service.mark_conversation_read(
        conversation_id=conversation_id,
        reader_id=current_user.id,
    )
