from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from utils.sanitize import sanitize_string

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

    @field_validator('content')
    @classmethod
    def sanitize_content(cls, v):
        return sanitize_string(v, max_length=2000)

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    participant_id: int
    booking_id: Optional[int] = None
    initial_message: Optional[str] = Field(None, max_length=2000)

    @field_validator('initial_message')
    @classmethod
    def sanitize_message(cls, v):
        if v:
            return sanitize_string(v, max_length=2000)
        return v

class ConversationResponse(BaseModel):
    id: int
    participant_one_id: int
    participant_two_id: int
    booking_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0

    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationResponse):
    messages: List[MessageResponse] = []
