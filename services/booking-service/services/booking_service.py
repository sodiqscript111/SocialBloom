from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.booking import Booking
from app.models.booking import Booking
from app.schemas.booking import BookingCreate
from events.producer import creator_notification, business_notification
class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: BookingCreate) -> Booking:
        # Validate that both users exist
        self._verify_user_exists(booking.business_id, "Business")
        self._verify_user_exists(booking.creator_id, "Creator")

        new_booking = Booking(
            business_id=booking.business_id,
            creator_id=booking.creator_id,
            price=booking.price,
            requirements=booking.requirements
        )
        self.db.add(new_booking)
        self.db.commit()
        self.db.refresh(new_booking)
        
        # Trigger Kafka event (Notification)
        creator_notification(booking.creator_id)
        business_notification(booking.business_id)
        
        return new_booking

    def _verify_user_exists(self, user_id: int, role_label: str):
        import httpx
        try:
            # Connects to User Service on port 8000
            response = httpx.get(f"http://127.0.0.1:8000/users/{user_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"{role_label} (ID: {user_id}) not found.")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail=f"Unable to verify {role_label}. User Service Unavailable.")

    def get_bookings(self) -> List[Booking]:
        return self.db.query(Booking).all()