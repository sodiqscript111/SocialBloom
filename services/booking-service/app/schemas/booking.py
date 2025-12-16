from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    creator_id: int
    price: Decimal
    requirements: str

class BookingCreate(BookingBase):
    """Request model for creating a booking. business_id comes from JWT token."""
    pass

class BookingResponse(BaseModel):
    id: int
    business_id: int
    creator_id: int
    price: Decimal
    requirements: str
    status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
