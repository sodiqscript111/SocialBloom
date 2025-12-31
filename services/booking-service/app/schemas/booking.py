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
    campaign_id: Optional[int] = None

class BookingUpdate(BaseModel):
    price: Optional[Decimal] = None
    requirements: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class BookingResponse(BaseModel):
    id: int
    business_id: int
    creator_id: int
    price: Decimal
    requirements: str
    status: BookingStatus
    campaign_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
