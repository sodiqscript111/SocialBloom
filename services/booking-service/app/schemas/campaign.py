from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.models.campaign import CampaignStatus
from app.schemas.booking import BookingResponse

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    budget: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[CampaignStatus] = None

class CampaignResponse(CampaignBase):
    id: int
    business_id: int
    status: CampaignStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CampaignWithBookings(CampaignResponse):
    bookings: List[BookingResponse] = []
    total_spent: Decimal = Decimal("0.00")
    booking_count: int = 0
