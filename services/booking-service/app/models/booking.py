from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from db.database import Base

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PAID = "paid"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

VALID_STATUS_TRANSITIONS = {
    BookingStatus.PENDING: [BookingStatus.ACCEPTED, BookingStatus.REJECTED, BookingStatus.CANCELLED],
    BookingStatus.ACCEPTED: [BookingStatus.PAID, BookingStatus.CANCELLED],
    BookingStatus.REJECTED: [],
    BookingStatus.PAID: [BookingStatus.DELIVERED, BookingStatus.CANCELLED],
    BookingStatus.DELIVERED: [BookingStatus.COMPLETED],
    BookingStatus.COMPLETED: [],
    BookingStatus.CANCELLED: [],
}

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, index=True)
    creator_id = Column(Integer, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)

    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    price = Column(DECIMAL(10, 2))
    requirements = Column(String)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    campaign = relationship("Campaign", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
