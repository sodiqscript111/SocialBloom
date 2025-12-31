from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from db.database import Base

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    budget = Column(DECIMAL(10, 2), nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bookings = relationship("Booking", back_populates="campaign")
