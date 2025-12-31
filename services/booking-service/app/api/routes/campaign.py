from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignWithBookings
from app.schemas.booking import BookingResponse
from services.campaign_service import CampaignService
from auth.dependencies import require_business_owner, TokenData


router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


def get_campaign_service(db: Session = Depends(get_db)) -> CampaignService:
    return CampaignService(db)


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: TokenData = Depends(require_business_owner),
    service: CampaignService = Depends(get_campaign_service)
):
    return service.create_campaign(campaign, current_user.user_id)


@router.get("", response_model=List[CampaignResponse])
async def get_campaigns(
    current_user: TokenData = Depends(require_business_owner),
    service: CampaignService = Depends(get_campaign_service)
):
    return service.get_campaigns(current_user.user_id)


@router.get("/{campaign_id}", response_model=CampaignWithBookings)
async def get_campaign(
    campaign_id: int,
    current_user: TokenData = Depends(require_business_owner),
    service: CampaignService = Depends(get_campaign_service)
):
    return service.get_campaign_by_id(campaign_id, current_user.user_id)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    update: CampaignUpdate,
    current_user: TokenData = Depends(require_business_owner),
    service: CampaignService = Depends(get_campaign_service)
):
    return service.update_campaign(campaign_id, update, current_user.user_id)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    current_user: TokenData = Depends(require_business_owner),
    service: CampaignService = Depends(get_campaign_service)
):
    service.delete_campaign(campaign_id, current_user.user_id)
    return None


@router.post("/{campaign_id}/bookings/{booking_id}", response_model=BookingResponse)
async def add_booking_to_campaign(
    campaign_id: int,
    booking_id: int,
    current_user: TokenData = Depends(require_business_owner),
    service: CampaignService = Depends(get_campaign_service)
):
    return service.add_booking_to_campaign(campaign_id, booking_id, current_user.user_id)


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: int,
    current_user: TokenData = Depends(require_business_owner),
    service: CampaignService = Depends(get_campaign_service)
):
    return service.get_campaign_stats(campaign_id, current_user.user_id)
