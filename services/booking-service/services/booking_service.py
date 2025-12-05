from typing import List
from sqlalchemy.orm import Session
from app.models.booking import Booking
from app.schemas.booking import BookingCreate
class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: BookingCreate) -> Booking:
        new_booking = Booking(
            business_id=booking.business_id,
            creator_id=booking.creator_id,
            price=booking.price,
            requirements=booking.requirements
        )
        self.db.add(new_booking)
        self.db.commit()
        self.db.refresh(new_booking)
        return new_booking

    def get_bookings(self) -> List[Booking]:
        return self.db.query(Booking).all()