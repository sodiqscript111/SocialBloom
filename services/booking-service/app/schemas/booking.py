from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.booking import BookingStatus
from utils.sanitize import sanitize_string

class BookingBase(BaseModel):
    creator_id: int
    price: Decimal = Field(..., gt=0, le=1000000)
    requirements: str = Field(..., min_length=1, max_length=2000)

    @field_validator('requirements')
    @classmethod
    def sanitize_requirements(cls, v):
        return sanitize_string(v, max_length=2000)

class BookingCreate(BookingBase):
    campaign_id: Optional[int] = None

class BookingUpdate(BaseModel):
    price: Optional[Decimal] = Field(None, gt=0, le=1000000)
    requirements: Optional[str] = Field(None, min_length=1, max_length=2000)

    @field_validator('requirements')
    @classmethod
    def sanitize_requirements(cls, v):
        if v:
            return sanitize_string(v, max_length=2000)
        return v

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
