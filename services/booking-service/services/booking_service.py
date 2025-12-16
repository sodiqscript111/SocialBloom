from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.booking import Booking
from app.schemas.booking import BookingCreate
from events.producer import creator_notification, business_notification


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: BookingCreate, business_id: int) -> Booking:
        """
        Create a new booking.
        
        Args:
            booking: Booking data from request
            business_id: ID of the authenticated business owner (from JWT)
            
        Returns:
            Created booking object
        """
        new_booking = Booking(
            business_id=business_id,  # From JWT token
            creator_id=booking.creator_id,
            price=booking.price,
            requirements=booking.requirements
        )
        self.db.add(new_booking)
        self.db.commit()
        self.db.refresh(new_booking)
        
        # Trigger Kafka event (Notification)
        creator_notification(booking.creator_id)
        business_notification(business_id)
        
        return new_booking

    def get_bookings(self) -> List[Booking]:
        return self.db.query(Booking).all()