from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime

class NotificationType(str, Enum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    PAYMENT_RECEIVED = "payment_received"
    NEW_MESSAGE = "new_message"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class NotificationBase(BaseModel):
    user_id: int
    type: NotificationType
    message: str
    channel: str = "email"  # 'email', 'sms', 'push'

class NotificationCreate(NotificationBase):
    """
    Schema for creating a new notification (e.g. from Kafka consumer)
    """
    recipient_email: Optional[EmailStr] = None 
    recipient_phone: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True
