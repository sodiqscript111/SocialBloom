from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    booking_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None

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
