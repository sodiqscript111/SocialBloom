from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db, engine
from app.models.booking import Booking, Base
from app.schemas.booking import BookingCreate, BookingResponse
from services.booking_service import BookingService
from auth.dependencies import get_current_user, require_business_owner, TokenData

Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    return BookingService(db)

@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate, 
    current_user: TokenData = Depends(require_business_owner),
    service: BookingService = Depends(get_booking_service)
):
    return service.create_booking(booking, business_id=current_user.user_id)

@router.get("/bookings", response_model=List[BookingResponse])
async def get_bookings(
    current_user: TokenData = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service)
):
    return service.get_bookings()
