from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from fastapi import HTTPException, status
from app.models.chat import Conversation, Message
from app.models.notification import Notification, NotificationType
from app.schemas.chat import ConversationCreate, MessageCreate, ConversationResponse, MessageResponse


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def _create_message_notification(self, recipient_id: int, sender_id: int, conversation_id: int):
        notification = Notification(
            user_id=recipient_id,
            type=NotificationType.NEW_MESSAGE,
            title="New Message",
            message="You have received a new message",
            data={"conversation_id": conversation_id, "sender_id": sender_id}
        )
        self.db.add(notification)

    def get_or_create_conversation(
        self, user_id: int, participant_id: int, booking_id: Optional[int] = None
    ) -> Conversation:
        conversation = self.db.query(Conversation).filter(
            or_(
                and_(
                    Conversation.participant_one_id == user_id,
                    Conversation.participant_two_id == participant_id
                ),
                and_(
                    Conversation.participant_one_id == participant_id,
                    Conversation.participant_two_id == user_id
                )
            )
        ).first()

        if not conversation:
            conversation = Conversation(
                participant_one_id=user_id,
                participant_two_id=participant_id,
                booking_id=booking_id
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)

        return conversation

    def start_conversation(self, user_id: int, data: ConversationCreate) -> Conversation:
        conversation = self.get_or_create_conversation(
            user_id, data.participant_id, data.booking_id
        )

        if data.initial_message:
            message = Message(
                conversation_id=conversation.id,
                sender_id=user_id,
                content=data.initial_message
            )
            self.db.add(message)
            self._create_message_notification(data.participant_id, user_id, conversation.id)
            self.db.commit()

        return conversation

    def get_user_conversations(self, user_id: int) -> List[ConversationResponse]:
        conversations = self.db.query(Conversation).filter(
            or_(
                Conversation.participant_one_id == user_id,
                Conversation.participant_two_id == user_id
            )
        ).order_by(desc(Conversation.updated_at)).all()

        result = []
        for conv in conversations:
            last_message = self.db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(desc(Message.created_at)).first()

            unread_count = self.db.query(Message).filter(
                Message.conversation_id == conv.id,
                Message.sender_id != user_id,
                Message.is_read == False
            ).count()

            result.append(ConversationResponse(
                id=conv.id,
                participant_one_id=conv.participant_one_id,
                participant_two_id=conv.participant_two_id,
                booking_id=conv.booking_id,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                last_message=MessageResponse.model_validate(last_message) if last_message else None,
                unread_count=unread_count
            ))

        return result

    def get_conversation(self, conversation_id: int, user_id: int) -> Conversation:
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.participant_one_id != user_id and conversation.participant_two_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return conversation

    def get_messages(
        self, conversation_id: int, user_id: int, limit: int = 50, before_id: Optional[int] = None
    ) -> List[Message]:
        self.get_conversation(conversation_id, user_id)

        query = self.db.query(Message).filter(Message.conversation_id == conversation_id)

        if before_id:
            query = query.filter(Message.id < before_id)

        return query.order_by(desc(Message.created_at)).limit(limit).all()

    def send_message(self, conversation_id: int, user_id: int, data: MessageCreate) -> Message:
        conversation = self.get_conversation(conversation_id, user_id)

        message = Message(
            conversation_id=conversation_id,
            sender_id=user_id,
            content=data.content
        )

        self.db.add(message)

        recipient_id = conversation.participant_two_id if conversation.participant_one_id == user_id else conversation.participant_one_id
        self._create_message_notification(recipient_id, user_id, conversation_id)

        self.db.commit()
        self.db.refresh(message)

        return message

    def mark_messages_as_read(self, conversation_id: int, user_id: int) -> int:
        self.get_conversation(conversation_id, user_id)

        count = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read == False
        ).update({Message.is_read: True}, synchronize_session=False)

        self.db.commit()
        return count

    def get_unread_count(self, user_id: int) -> int:
        conversations = self.db.query(Conversation).filter(
            or_(
                Conversation.participant_one_id == user_id,
                Conversation.participant_two_id == user_id
            )
        ).all()

        conversation_ids = [c.id for c in conversations]

        return self.db.query(Message).filter(
            Message.conversation_id.in_(conversation_ids),
            Message.sender_id != user_id,
            Message.is_read == False
        ).count()
