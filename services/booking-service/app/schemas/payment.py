from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentMethod

class PaymentCreate(BaseModel):
    booking_id: int
    amount: Decimal
    payment_method: PaymentMethod = PaymentMethod.CARD
    currency: str = "USD"

class PaymentCapture(BaseModel):
    pass

class PaymentRefund(BaseModel):
    reason: str

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    refund_reason: Optional[str] = None
    created_at: datetime
    captured_at: Optional[datetime] = None
    released_at: Optional[datetime] = None

    class Config:
        from_attributes = True
