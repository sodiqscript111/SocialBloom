from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from ..models.user import UserRole, SocialPlatform

# --- Social Connection Schemas ---
class SocialConnectionBase(BaseModel):
    platform: SocialPlatform
    platform_username: str
    profile_url: str

class SocialConnectionCreate(SocialConnectionBase):
    access_token: str

class SocialConnectionResponse(BaseModel):
    id: int
    platform: SocialPlatform
    platform_user_id: Optional[str] = None
    platform_username: str
    display_name: Optional[str] = None
    profile_url: str
    avatar_url: Optional[str] = None
    follower_count: int
    connected_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Creator Profile Schemas ---
class CreatorProfileBase(BaseModel):
    intro_video_url: Optional[str] = None
    price_per_video: Optional[Decimal] = None
    capacity_limit: int = 5
    capacity_window: str = "Weekly"
    niche: Optional[str] = None

class CreatorProfileCreate(CreatorProfileBase):
    pass

class CreatorProfileResponse(CreatorProfileBase):
    id: int

    class Config:
        from_attributes = True

# --- Update Schemas ---
class CreatorProfileUpdate(BaseModel):
    intro_video_url: Optional[str] = None
    price_per_video: Optional[Decimal] = None
    capacity_limit: Optional[int] = None
    capacity_window: Optional[str] = None
    niche: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    creator_profile: Optional[CreatorProfileUpdate] = None


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str
    # Optional: Creator details can be sent during registration
    creator_profile: Optional[CreatorProfileCreate] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    creator_profile: Optional[CreatorProfileResponse] = None
    social_connections: List[SocialConnectionResponse] = []

    class Config:
        from_attributes = True


# --- Token Schemas ---
class Token(BaseModel):
    """Response model for login endpoint."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Request model for token refresh."""
    refresh_token: str