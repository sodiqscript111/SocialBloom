from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class CreatorSearchFilters(BaseModel):
    niche: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_followers: Optional[int] = None
    platform: Optional[str] = None

class CreatorSearchResult(BaseModel):
    id: int
    email: str
    niche: Optional[str] = None
    price_per_video: Optional[Decimal] = None
    capacity_limit: int = 5
    capacity_window: str = "Weekly"
    total_followers: int = 0
    platforms: List[str] = []

    class Config:
        from_attributes = True

class SavedCreatorCreate(BaseModel):
    creator_id: int
    notes: Optional[str] = None

class SavedCreatorResponse(BaseModel):
    id: int
    business_id: int
    creator_id: int
    notes: Optional[str] = None
    saved_at: datetime
    creator: Optional[CreatorSearchResult] = None

    class Config:
        from_attributes = True
