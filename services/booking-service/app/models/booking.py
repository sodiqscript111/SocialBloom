from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, ForeignKey
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

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, index=True) # ID from user-service
    creator_id = Column(Integer, index=True)  # ID from user-service
    
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    price = Column(DECIMAL(10, 2))
    requirements = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
