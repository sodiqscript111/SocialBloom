from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db, engine
from app.models.booking import Booking, Base
from app.schemas.booking import BookingCreate, BookingResponse

# Create tables (Simplification for now, usually done via Alembic)
Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = Booking(
        business_id=booking.business_id,
        creator_id=booking.creator_id,
        price=booking.price,
        requirements=booking.requirements
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/bookings", response_model=List[BookingResponse])
async def get_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()
