from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
import httpx
from app.models.booking import Booking
from app.schemas.booking import BookingCreate
class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: BookingCreate) -> Booking:
        # Verify User Exists
        self._verify_user(booking.creator_id)
        # Verify Business Exists
        self._verify_user(booking.business_id) 

        new_booking = Booking(
            business_id=booking.business_id,
            creator_id=booking.creator_id,
            price=booking.price,
            requirements=booking.requirements
        )
        self.db.add(new_booking)
        self.db.commit()
        self.db.refresh(new_booking)
        
        self.db.refresh(new_booking)
        
        return new_booking

    def _verify_user(self, user_id: int):
        try:
            # Assuming User Service runs on port 8000
            response = httpx.get(f"http://127.0.0.1:8000/users/{user_id}")
            if response.status_code != 200:
                print(f"User validation failed for {user_id}: Status {response.status_code}", flush=True)
                raise HTTPException(status_code=400, detail=f"User with ID {user_id} does not exist")
        except httpx.RequestError as e:
            print(f"Error connecting to User Service: {e}", flush=True)
            raise HTTPException(status_code=503, detail="User Service unavailable")
        except HTTPException:
            raise
        except Exception as e:
            print(f"Unexpected error verifying user: {e}", flush=True)
            raise HTTPException(status_code=500, detail=f"Error verifying user: {str(e)}")

        return True

    def get_bookings(self, business_id: int = None, creator_id: int = None, status: str = None) -> List[Booking]:
        query = self.db.query(Booking)
        if business_id:
            query = query.filter(Booking.business_id == business_id)
        if creator_id:
            query = query.filter(Booking.creator_id == creator_id)
        if status:
            query = query.filter(Booking.status == status)
        return query.all()

    def get_booking_by_id(self, booking_id: int) -> Booking:
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking

    def update_booking_status(self, booking_id: int, status: str) -> Booking:
        booking = self.get_booking_by_id(booking_id)
        booking.status = status
        self.db.commit()
        self.db.refresh(booking)
        return booking