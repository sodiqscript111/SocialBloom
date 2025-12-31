from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db, engine
from app.models.booking import Booking, Base
from app.schemas.booking import BookingCreate, BookingUpdate, BookingStatusUpdate, BookingResponse
from services.booking_service import BookingService
from auth.dependencies import get_current_user, require_business_owner, require_creator, TokenData

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/bookings", tags=["Bookings"])

def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    return BookingService(db)

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    current_user: TokenData = Depends(require_business_owner),
    service: BookingService = Depends(get_booking_service)
):
    return service.create_booking(booking, business_id=current_user.user_id)

@router.get("", response_model=List[BookingResponse])
async def get_bookings(
    current_user: TokenData = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service)
):
    return service.get_bookings()

@router.get("/my", response_model=List[BookingResponse])
async def get_my_bookings(
    current_user: TokenData = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service)
):
    return service.get_user_bookings(current_user.user_id, current_user.role)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service)
):
    return service.get_booking_by_id(booking_id, current_user.user_id, current_user.role)

@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    update_data: BookingUpdate,
    current_user: TokenData = Depends(require_business_owner),
    service: BookingService = Depends(get_booking_service)
):
    return service.update_booking(booking_id, update_data, current_user.user_id)

@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    current_user: TokenData = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service)
):
    return service.update_booking_status(
        booking_id, status_update, current_user.user_id, current_user.role
    )

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    current_user: TokenData = Depends(require_business_owner),
    service: BookingService = Depends(get_booking_service)
):
    service.delete_booking(booking_id, current_user.user_id)
    return None
