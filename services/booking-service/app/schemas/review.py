from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from utils.sanitize import sanitize_string

class ReviewCreate(BaseModel):
    booking_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000)

    @field_validator('comment')
    @classmethod
    def sanitize_comment(cls, v):
        if v:
            return sanitize_string(v, max_length=1000)
        return v

class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    reviewer_id: int
    reviewed_id: int
    reviewer_role: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserRatingStats(BaseModel):
    user_id: int
    average_rating: float
    total_reviews: int
    rating_breakdown: dict
