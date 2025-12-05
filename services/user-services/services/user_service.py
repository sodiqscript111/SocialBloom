from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, CreatorProfile, UserRole
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from utils.password_hasher import hash_password, verify_password

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> User:
        # Check if user already exists
        db_user = self.db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email already registered"
            )
        
        # Create new user
        new_user = User(
            email=user.email,
            password_hash=hash_password(user.password),
            role=user.role
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, user_login: UserLogin) -> User:
        db_user = self.db.query(User).filter(User.email == user_login.email).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )
        if not verify_password(user_login.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )
        return db_user

    def get_users(self) -> List[User]:
        return self.db.query(User).all()
    
    def get_user_by_id(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        # Update basic user info
        if user_update.email:
            db_user.email = user_update.email
        if user_update.role:
            db_user.role = user_update.role
            
        # Handle creator profile updates
        if user_update.creator_profile and db_user.role == UserRole.CREATOR:
            if not db_user.creator_profile:
                # Create profile if it doesn't exist
                db_profile = CreatorProfile(user_id=db_user.id)
                self.db.add(db_profile)
                db_user.creator_profile = db_profile
            
            # Update profile fields
            profile_data = user_update.creator_profile.dict(exclude_unset=True)
            for key, value in profile_data.items():
                setattr(db_user.creator_profile, key, value)
                
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_creators(
        self, 
        niche: Optional[str] = None, 
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None
    ) -> List[User]:
        query = self.db.query(User).join(CreatorProfile).filter(User.role == UserRole.CREATOR)
        
        if niche:
            query = query.filter(CreatorProfile.niche.ilike(f"%{niche}%"))
        
        if min_price is not None:
            query = query.filter(CreatorProfile.price_per_video >= min_price)
            
        if max_price is not None:
            query = query.filter(CreatorProfile.price_per_video <= max_price)
            
        return query.all()  
    
    def delete_user(self, user_id: int) -> None:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        self.db.delete(db_user)
        self.db.commit()
        return db_user