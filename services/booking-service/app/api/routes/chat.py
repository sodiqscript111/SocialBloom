from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from app.schemas.chat import (
    ConversationCreate, ConversationResponse, ConversationWithMessages,
    MessageCreate, MessageResponse
)
from services.chat_service import ChatService
from auth.dependencies import get_current_user, TokenData


router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


@router.post("/conversations", response_model=ConversationResponse)
async def start_conversation(
    data: ConversationCreate,
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    return service.start_conversation(current_user.user_id, data)


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    return service.get_user_conversations(current_user.user_id)


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100),
    before_id: Optional[int] = Query(None, description="Get messages before this ID for pagination"),
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    return service.get_messages(conversation_id, current_user.user_id, limit, before_id)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    message: MessageCreate,
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    return service.send_message(conversation_id, current_user.user_id, message)


@router.post("/conversations/{conversation_id}/read")
async def mark_as_read(
    conversation_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    count = service.mark_messages_as_read(conversation_id, current_user.user_id)
    return {"marked_as_read": count}


@router.get("/unread/count")
async def get_unread_count(
    current_user: TokenData = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service)
):
    return {"unread_count": service.get_unread_count(current_user.user_id)}
