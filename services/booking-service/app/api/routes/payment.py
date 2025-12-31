from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from app.schemas.payment import PaymentCreate, PaymentRefund, PaymentResponse
from services.payment_service import PaymentService
from auth.dependencies import get_current_user, require_business_owner, TokenData


router = APIRouter(prefix="/payments", tags=["Payments"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    current_user: TokenData = Depends(require_business_owner),
    service: PaymentService = Depends(get_payment_service)
):
    return service.create_payment(payment, current_user.user_id)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service)
):
    return service.get_payment(payment_id, current_user.user_id)


@router.get("/booking/{booking_id}", response_model=PaymentResponse)
async def get_payment_by_booking(
    booking_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service)
):
    return service.get_payment_by_booking(booking_id, current_user.user_id)


@router.post("/{payment_id}/capture", response_model=PaymentResponse)
async def capture_payment(
    payment_id: int,
    current_user: TokenData = Depends(require_business_owner),
    service: PaymentService = Depends(get_payment_service)
):
    return service.capture_payment(payment_id, current_user.user_id)


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: int,
    refund_data: PaymentRefund,
    current_user: TokenData = Depends(require_business_owner),
    service: PaymentService = Depends(get_payment_service)
):
    return service.refund_payment(payment_id, refund_data, current_user.user_id)
