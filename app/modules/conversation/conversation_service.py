from datetime import UTC, datetime
import uuid

from sqlalchemy.orm import Session

from app.modules.conversation.conversation_models import Conversation, Message
from app.modules.properties.property_models import Property
from app.utils.exceptions import AppError


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_conversation(
        self,
        property_id: uuid.UUID,
        user_a: uuid.UUID,
        user_b: uuid.UUID,
    ) -> Conversation:
        property = self.db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise AppError(404, "Property not found")

        user_one_id, user_two_id = sorted([user_a, user_b])

        conversation = self.db.query(Conversation).filter_by(
            user_one_id=user_one_id,
            user_two_id=user_two_id,
            property_id=property_id,
        ).first()

        if not conversation:
            conversation = Conversation(
                user_one_id=user_one_id,
                user_two_id=user_two_id,
                property_id=property_id,
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

        return conversation

    def resolve_unread_count(self, conversation: Conversation, user_id: uuid.UUID) -> int:
        if user_id == conversation.user_one_id:
            return conversation.unread_count_one
        return conversation.unread_count_two

    def get_user_conversations(self, user_id: uuid.UUID) -> list[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(
                (Conversation.user_one_id == user_id) |
                (Conversation.user_two_id == user_id)
            )
            .order_by(Conversation.last_message_at.desc().nullslast())
            .all()
        )

    def send_message(
        self,
        conversation_id: uuid.UUID,
        sender_id: uuid.UUID,
        content: str,
    ) -> Message:
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise AppError(404, "Conversation not found")

        if sender_id not in (conversation.user_one_id, conversation.user_two_id):
            raise AppError(403, "You are not a participant in this conversation")

        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            content=content,
        )
        self.db.add(message)

        conversation.last_message_text = content
        conversation.last_message_at = datetime.now(UTC)

        if sender_id == conversation.user_one_id:
            conversation.unread_count_two += 1
        else:
            conversation.unread_count_one += 1

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_conversation_messages(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 50,
        before: datetime | None = None,
    ) -> list[Message]:
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise AppError(404, "Conversation not found")

        if user_id not in (conversation.user_one_id, conversation.user_two_id):
            raise AppError(403, "User is not a participant in this conversation")

        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)

        if before:
            query = query.filter(Message.created_at < before)

        return query.order_by(Message.created_at.desc()).limit(limit).all()

    def mark_conversation_read(
        self,
        conversation_id: uuid.UUID,
        reader_id: uuid.UUID,
    ) -> None:
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise AppError(404, "Conversation not found")

        if reader_id not in (conversation.user_one_id, conversation.user_two_id):
            raise AppError(403, "User is not a participant in this conversation")

        if reader_id == conversation.user_one_id:
            conversation.unread_count_one = 0
        else:
            conversation.unread_count_two = 0

        self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != reader_id,
            Message.is_read == False,
        ).update({"is_read": True})

        self.db.commit()
