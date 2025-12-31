from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.payment import PaymentCreate, PaymentRefund
from events.producer import emit_booking_payment_completed


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_transaction_id(self) -> str:
        return f"txn_{uuid.uuid4().hex[:16]}"

    def _mock_payment_processor(self, amount: float, action: str) -> dict:
        return {
            "success": True,
            "transaction_id": self._generate_transaction_id(),
            "amount": amount,
            "action": action
        }

    def create_payment(self, payment_data: PaymentCreate, business_id: int) -> Payment:
        booking = self.db.query(Booking).filter(
            Booking.id == payment_data.booking_id,
            Booking.business_id == business_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found or access denied"
            )

        if booking.status != BookingStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment can only be created for accepted bookings"
            )

        existing_payment = self.db.query(Payment).filter(
            Payment.booking_id == payment_data.booking_id
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already exists for this booking"
            )

        result = self._mock_payment_processor(float(payment_data.amount), "hold")

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment processing failed"
            )

        payment = Payment(
            booking_id=payment_data.booking_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            payment_method=payment_data.payment_method,
            status=PaymentStatus.HELD,
            transaction_id=result["transaction_id"]
        )

        self.db.add(payment)

        booking.status = BookingStatus.PAID
        self.db.commit()
        self.db.refresh(payment)

        emit_booking_payment_completed(booking.id, payment.id, float(payment.amount))

        return payment

    def get_payment(self, payment_id: int, user_id: int) -> Payment:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        booking = self.db.query(Booking).filter(Booking.id == payment.booking_id).first()

        if booking.business_id != user_id and booking.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return payment

    def get_payment_by_booking(self, booking_id: int, user_id: int) -> Payment:
        booking = self.db.query(Booking).filter(
            Booking.id == booking_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.business_id != user_id and booking.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        payment = self.db.query(Payment).filter(Payment.booking_id == booking_id).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payment found for this booking"
            )

        return payment

    def capture_payment(self, payment_id: int, business_id: int) -> Payment:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        booking = self.db.query(Booking).filter(Booking.id == payment.booking_id).first()

        if booking.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        if payment.status != PaymentStatus.HELD:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot capture payment with status {payment.status.value}"
            )

        if booking.status != BookingStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment can only be captured after delivery is confirmed"
            )

        result = self._mock_payment_processor(float(payment.amount), "capture")

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment capture failed"
            )

        payment.status = PaymentStatus.RELEASED
        payment.released_at = datetime.utcnow()

        booking.status = BookingStatus.COMPLETED
        self.db.commit()
        self.db.refresh(payment)

        return payment

    def refund_payment(self, payment_id: int, refund_data: PaymentRefund, business_id: int) -> Payment:
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        booking = self.db.query(Booking).filter(Booking.id == payment.booking_id).first()

        if booking.business_id != business_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        if payment.status not in [PaymentStatus.HELD, PaymentStatus.RELEASED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot refund payment with status {payment.status.value}"
            )

        result = self._mock_payment_processor(float(payment.amount), "refund")

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund processing failed"
            )

        payment.status = PaymentStatus.REFUNDED
        payment.refund_reason = refund_data.reason

        booking.status = BookingStatus.CANCELLED
        self.db.commit()
        self.db.refresh(payment)

        return payment
