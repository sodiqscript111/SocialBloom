import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from db import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    data = Column(String, nullable=True) # Storing as string representation of JSON for simplicity
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
