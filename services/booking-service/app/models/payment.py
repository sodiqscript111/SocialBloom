from sqlalchemy import Column, Integer, String, Enum, DECIMAL, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from db.database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    HELD = "held"
    CAPTURED = "captured"
    RELEASED = "released"
    REFUNDED = "refunded"
    FAILED = "failed"

class PaymentMethod(str, enum.Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CARD)
    transaction_id = Column(String, nullable=True)
    refund_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    captured_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)

    booking = relationship("Booking", back_populates="payment")
