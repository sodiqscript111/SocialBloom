from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from fastapi import HTTPException, status
from app.models.user import User, CreatorProfile, UserRole, SocialConnection
from app.models.matching import SavedCreator
from app.schemas.matching import CreatorSearchFilters, CreatorSearchResult, SavedCreatorCreate


class MatchingService:
    def __init__(self, db: Session):
        self.db = db

    def search_creators(self, filters: CreatorSearchFilters) -> List[CreatorSearchResult]:
        query = self.db.query(User).join(CreatorProfile).filter(User.role == UserRole.CREATOR)

        if filters.niche:
            query = query.filter(CreatorProfile.niche.ilike(f"%{filters.niche}%"))

        if filters.min_price is not None:
            query = query.filter(CreatorProfile.price_per_video >= filters.min_price)

        if filters.max_price is not None:
            query = query.filter(CreatorProfile.price_per_video <= filters.max_price)

        creators = query.all()
        results = []

        for creator in creators:
            connections = self.db.query(SocialConnection).filter(
                SocialConnection.user_id == creator.id
            ).all()

            total_followers = sum(c.follower_count or 0 for c in connections)
            platforms = [c.platform.value for c in connections]

            if filters.min_followers and total_followers < filters.min_followers:
                continue

            if filters.platform and filters.platform.lower() not in [p.lower() for p in platforms]:
                continue

            profile = creator.creator_profile
            results.append(CreatorSearchResult(
                id=creator.id,
                email=creator.email,
                niche=profile.niche if profile else None,
                price_per_video=profile.price_per_video if profile else None,
                capacity_limit=profile.capacity_limit if profile else 5,
                capacity_window=profile.capacity_window if profile else "Weekly",
                total_followers=total_followers,
                platforms=platforms
            ))

        return results

    def get_recommended_creators(self, business_id: int, limit: int = 10) -> List[CreatorSearchResult]:
        saved = self.db.query(SavedCreator.creator_id).filter(
            SavedCreator.business_id == business_id
        ).all()
        saved_ids = [s.creator_id for s in saved]

        query = self.db.query(User).join(CreatorProfile).filter(
            User.role == UserRole.CREATOR
        )

        if saved_ids:
            query = query.filter(~User.id.in_(saved_ids))

        creators = query.limit(limit).all()
        results = []

        for creator in creators:
            connections = self.db.query(SocialConnection).filter(
                SocialConnection.user_id == creator.id
            ).all()

            total_followers = sum(c.follower_count or 0 for c in connections)
            platforms = [c.platform.value for c in connections]

            profile = creator.creator_profile
            results.append(CreatorSearchResult(
                id=creator.id,
                email=creator.email,
                niche=profile.niche if profile else None,
                price_per_video=profile.price_per_video if profile else None,
                capacity_limit=profile.capacity_limit if profile else 5,
                capacity_window=profile.capacity_window if profile else "Weekly",
                total_followers=total_followers,
                platforms=platforms
            ))

        return results

    def save_creator(self, business_id: int, data: SavedCreatorCreate) -> SavedCreator:
        existing = self.db.query(SavedCreator).filter(
            SavedCreator.business_id == business_id,
            SavedCreator.creator_id == data.creator_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Creator already saved"
            )

        creator = self.db.query(User).filter(
            User.id == data.creator_id,
            User.role == UserRole.CREATOR
        ).first()

        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Creator not found"
            )

        saved = SavedCreator(
            business_id=business_id,
            creator_id=data.creator_id,
            notes=data.notes
        )
        self.db.add(saved)
        self.db.commit()
        self.db.refresh(saved)
        return saved

    def get_saved_creators(self, business_id: int) -> List[SavedCreator]:
        return self.db.query(SavedCreator).filter(
            SavedCreator.business_id == business_id
        ).all()

    def delete_saved_creator(self, business_id: int, creator_id: int) -> bool:
        saved = self.db.query(SavedCreator).filter(
            SavedCreator.business_id == business_id,
            SavedCreator.creator_id == creator_id
        ).first()

        if not saved:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved creator not found"
            )

        self.db.delete(saved)
        self.db.commit()
        return True
