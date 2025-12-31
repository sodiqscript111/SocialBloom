from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from db.database import Base

class SavedCreator(Base):
    __tablename__ = "saved_creators"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, index=True)
    creator_id = Column(Integer, index=True)
    notes = Column(Text, nullable=True)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())
