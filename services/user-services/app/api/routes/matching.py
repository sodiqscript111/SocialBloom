from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import get_db
from services.matching_service import MatchingService
from app.schemas.matching import (
    CreatorSearchFilters, 
    CreatorSearchResult, 
    SavedCreatorCreate, 
    SavedCreatorResponse
)
from utils.auth_dependencies import get_current_user, TokenData


router = APIRouter(prefix="/creators", tags=["Creator Matching"])


def get_matching_service(db: Session = Depends(get_db)) -> MatchingService:
    return MatchingService(db)


@router.get("/search", response_model=List[CreatorSearchResult])
async def search_creators(
    niche: Optional[str] = Query(None, description="Filter by niche"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price per video"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price per video"),
    min_followers: Optional[int] = Query(None, description="Minimum total followers"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    current_user: TokenData = Depends(get_current_user),
    service: MatchingService = Depends(get_matching_service)
):
    filters = CreatorSearchFilters(
        niche=niche,
        min_price=min_price,
        max_price=max_price,
        min_followers=min_followers,
        platform=platform
    )
    return service.search_creators(filters)


@router.get("/recommended", response_model=List[CreatorSearchResult])
async def get_recommended_creators(
    limit: int = Query(10, ge=1, le=50),
    current_user: TokenData = Depends(get_current_user),
    service: MatchingService = Depends(get_matching_service)
):
    return service.get_recommended_creators(current_user.user_id, limit)


@router.post("/saved", response_model=SavedCreatorResponse)
async def save_creator(
    data: SavedCreatorCreate,
    current_user: TokenData = Depends(get_current_user),
    service: MatchingService = Depends(get_matching_service)
):
    return service.save_creator(current_user.user_id, data)


@router.get("/saved", response_model=List[SavedCreatorResponse])
async def get_saved_creators(
    current_user: TokenData = Depends(get_current_user),
    service: MatchingService = Depends(get_matching_service)
):
    return service.get_saved_creators(current_user.user_id)


@router.delete("/saved/{creator_id}")
async def delete_saved_creator(
    creator_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: MatchingService = Depends(get_matching_service)
):
    service.delete_saved_creator(current_user.user_id, creator_id)
    return {"success": True, "message": "Creator removed from saved list"}
