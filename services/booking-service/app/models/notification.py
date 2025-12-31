from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
import enum
from db.database import Base

class NotificationType(str, enum.Enum):
    BOOKING_CREATED = "booking_created"
    BOOKING_ACCEPTED = "booking_accepted"
    BOOKING_REJECTED = "booking_rejected"
    BOOKING_PAID = "booking_paid"
    BOOKING_DELIVERED = "booking_delivered"
    BOOKING_COMPLETED = "booking_completed"
    BOOKING_CANCELLED = "booking_cancelled"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_RELEASED = "payment_released"
    PAYMENT_REFUNDED = "payment_refunded"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_ENDED = "campaign_ended"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(Enum(NotificationType))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
