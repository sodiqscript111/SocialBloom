from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from app.models.notification import NotificationType

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationList(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int

class MarkReadRequest(BaseModel):
    notification_ids: List[int]
