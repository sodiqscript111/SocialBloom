from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db, engine
from app.models.booking import Booking, Base
from app.schemas.booking import BookingCreate, BookingResponse
from services.booking_service import BookingService

# Create tables (Simplification for now, usually done via Alembic)
Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    return BookingService(db)

@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate, 
    service: BookingService = Depends(get_booking_service)
):
    return service.create_booking(booking)

@router.get("/bookings", response_model=List[BookingResponse])
async def get_bookings(
    service: BookingService = Depends(get_booking_service)
):
    return service.get_bookings()
