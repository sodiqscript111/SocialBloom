from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.campaign import Campaign, CampaignStatus
from app.models.booking import Booking
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignWithBookings


class CampaignService:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, campaign: CampaignCreate, business_id: int) -> Campaign:
        new_campaign = Campaign(
            business_id=business_id,
            name=campaign.name,
            description=campaign.description,
            budget=campaign.budget,
            start_date=campaign.start_date,
            end_date=campaign.end_date
        )
        self.db.add(new_campaign)
        self.db.commit()
        self.db.refresh(new_campaign)
        return new_campaign

    def get_campaigns(self, business_id: int) -> List[Campaign]:
        return self.db.query(Campaign).filter(
            Campaign.business_id == business_id,
            Campaign.is_deleted == False
        ).all()

    def get_campaign_by_id(self, campaign_id: int, business_id: int) -> CampaignWithBookings:
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.business_id == business_id,
            Campaign.is_deleted == False
        ).first()

        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        bookings = self.db.query(Booking).filter(
            Booking.campaign_id == campaign_id,
            Booking.is_deleted == False
        ).all()

        total_spent = sum(b.price for b in bookings if b.price)

        return CampaignWithBookings(
            id=campaign.id,
            business_id=campaign.business_id,
            name=campaign.name,
            description=campaign.description,
            budget=campaign.budget,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            status=campaign.status,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            bookings=bookings,
            total_spent=total_spent,
            booking_count=len(bookings)
        )

    def update_campaign(self, campaign_id: int, update: CampaignUpdate, business_id: int) -> Campaign:
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.business_id == business_id,
            Campaign.is_deleted == False
        ).first()

        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        if update.name is not None:
            campaign.name = update.name
        if update.description is not None:
            campaign.description = update.description
        if update.budget is not None:
            campaign.budget = update.budget
        if update.start_date is not None:
            campaign.start_date = update.start_date
        if update.end_date is not None:
            campaign.end_date = update.end_date
        if update.status is not None:
            campaign.status = update.status

        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def delete_campaign(self, campaign_id: int, business_id: int) -> bool:
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.business_id == business_id,
            Campaign.is_deleted == False
        ).first()

        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        campaign.is_deleted = True
        campaign.status = CampaignStatus.CANCELLED
        self.db.commit()
        return True

    def add_booking_to_campaign(self, campaign_id: int, booking_id: int, business_id: int) -> Booking:
        campaign = self.db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.business_id == business_id,
            Campaign.is_deleted == False
        ).first()

        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        booking = self.db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.business_id == business_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        booking.campaign_id = campaign_id
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_campaign_stats(self, campaign_id: int, business_id: int) -> dict:
        campaign = self.get_campaign_by_id(campaign_id, business_id)

        status_counts = {}
        for booking in campaign.bookings:
            s = booking.status.value if hasattr(booking.status, 'value') else booking.status
            status_counts[s] = status_counts.get(s, 0) + 1

        return {
            "campaign_id": campaign.id,
            "name": campaign.name,
            "budget": campaign.budget,
            "total_spent": campaign.total_spent,
            "remaining_budget": (campaign.budget or Decimal("0")) - campaign.total_spent,
            "booking_count": campaign.booking_count,
            "status_breakdown": status_counts
        }
