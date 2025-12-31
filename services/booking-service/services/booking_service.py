from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.booking import Booking, BookingStatus, VALID_STATUS_TRANSITIONS
from app.schemas.booking import BookingCreate, BookingUpdate, BookingStatusUpdate
from events.producer import (
    emit_booking_created,
    emit_booking_status_changed,
    creator_notification,
    business_notification
)


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: BookingCreate, business_id: int) -> Booking:
        new_booking = Booking(
            business_id=business_id,
            creator_id=booking.creator_id,
            price=booking.price,
            requirements=booking.requirements,
            campaign_id=booking.campaign_id
        )
        self.db.add(new_booking)
        self.db.commit()
        self.db.refresh(new_booking)

        emit_booking_created(new_booking.id, booking.creator_id, business_id)
        creator_notification(booking.creator_id, new_booking.id, "new_booking")

        return new_booking

    def get_booking_by_id(self, booking_id: int, user_id: int, role: str) -> Booking:
        booking = self.db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if role == "business_owner" and booking.business_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        if role == "creator" and booking.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return booking

    def get_bookings(self) -> List[Booking]:
        return self.db.query(Booking).filter(Booking.is_deleted == False).all()

    def get_user_bookings(self, user_id: int, role: str) -> List[Booking]:
        query = self.db.query(Booking).filter(Booking.is_deleted == False)

        if role == "business_owner":
            query = query.filter(Booking.business_id == user_id)
        elif role == "creator":
            query = query.filter(Booking.creator_id == user_id)

        return query.all()

    def update_booking(self, booking_id: int, update_data: BookingUpdate, user_id: int) -> Booking:
        booking = self.db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.business_id == user_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found or access denied"
            )

        if booking.status != BookingStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update pending bookings"
            )

        if update_data.price is not None:
            booking.price = update_data.price
        if update_data.requirements is not None:
            booking.requirements = update_data.requirements

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_booking_status(
        self, booking_id: int, status_update: BookingStatusUpdate, user_id: int, role: str
    ) -> Booking:
        booking = self.db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if role == "creator" and booking.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        if role == "business_owner" and booking.business_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        new_status = status_update.status
        if new_status not in VALID_STATUS_TRANSITIONS.get(booking.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {booking.status.value} to {new_status.value}"
            )

        creator_allowed = [BookingStatus.ACCEPTED, BookingStatus.REJECTED, BookingStatus.DELIVERED]
        business_allowed = [BookingStatus.COMPLETED, BookingStatus.CANCELLED, BookingStatus.PAID]

        if role == "creator" and new_status not in creator_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Creators cannot set status to {new_status.value}"
            )
        if role == "business_owner" and new_status not in business_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Business owners cannot set status to {new_status.value}"
            )

        old_status = booking.status
        booking.status = new_status
        self.db.commit()
        self.db.refresh(booking)

        emit_booking_status_changed(booking_id, old_status.value, new_status.value, user_id)

        if role == "creator":
            business_notification(booking.business_id, booking_id, f"booking_{new_status.value}")
        else:
            creator_notification(booking.creator_id, booking_id, f"booking_{new_status.value}")

        return booking

    def delete_booking(self, booking_id: int, user_id: int) -> bool:
        booking = self.db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.business_id == user_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found or access denied"
            )

        if booking.status not in [BookingStatus.PENDING, BookingStatus.REJECTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only delete pending or rejected bookings"
            )

        booking.is_deleted = True
        self.db.commit()
        return True