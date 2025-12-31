from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.models.campaign import CampaignStatus
from app.schemas.booking import BookingResponse
from utils.sanitize import sanitize_string

class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    budget: Optional[Decimal] = Field(None, gt=0, le=10000000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        return sanitize_string(v, max_length=200)

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v):
        if v:
            return sanitize_string(v, max_length=2000)
        return v

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    budget: Optional[Decimal] = Field(None, gt=0, le=10000000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[CampaignStatus] = None

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        if v:
            return sanitize_string(v, max_length=200)
        return v

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v):
        if v:
            return sanitize_string(v, max_length=2000)
        return v

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
