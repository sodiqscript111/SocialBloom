from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from db.database import Base


class UserRole(str, enum.Enum):
    BUSINESS_OWNER = "business_owner"
    CREATOR = "creator"


class SocialPlatform(str, enum.Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(UserRole))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    creator_profile = relationship("CreatorProfile", back_populates="user", uselist=False)
    social_connections = relationship("SocialConnection", back_populates="user", cascade="all, delete-orphan")

class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    intro_video_url = Column(String, nullable=True)
    price_per_video = Column(DECIMAL(10, 2), nullable=True) 
    
    
    capacity_limit = Column(Integer, default=5)
    capacity_window = Column(String, default="Weekly") 
    
    niche = Column(String, nullable=True) 

    
    user = relationship("User", back_populates="creator_profile")

class SocialConnection(Base):
    __tablename__ = "social_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    platform = Column(Enum(SocialPlatform))
    platform_user_id = Column(String, nullable=True)  # Platform's unique user ID
    platform_username = Column(String)
    display_name = Column(String, nullable=True)
    follower_count = Column(Integer, default=0)
    profile_url = Column(String)
    avatar_url = Column(String, nullable=True)
    
    # OAuth tokens
    access_token = Column(String)
    refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    
    user = relationship("User", back_populates="social_connections")
