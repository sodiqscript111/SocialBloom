from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    business_id: int
    creator_id: int
    price: Decimal
    requirements: str

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
