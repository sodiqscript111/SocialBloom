from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationList


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[dict] = None
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> NotificationList:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        total = query.count()
        unread_count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

        return NotificationList(
            notifications=notifications,
            total=total,
            unread_count=unread_count
        )

    def get_unread_count(self, user_id: int) -> int:
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    def mark_as_read(self, notification_id: int, user_id: int) -> Notification:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_multiple_as_read(self, notification_ids: List[int], user_id: int) -> int:
        result = self.db.query(Notification).filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id
        ).update({Notification.is_read: True}, synchronize_session=False)

        self.db.commit()
        return result

    def mark_all_as_read(self, user_id: int) -> int:
        result = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({Notification.is_read: True}, synchronize_session=False)

        self.db.commit()
        return result


def create_booking_notification(db: Session, user_id: int, booking_id: int, event_type: str):
    service = NotificationService(db)

    notification_map = {
        "booking_created": (NotificationType.BOOKING_CREATED, "New Booking Request", "You have received a new booking request"),
        "booking_accepted": (NotificationType.BOOKING_ACCEPTED, "Booking Accepted", "Your booking has been accepted"),
        "booking_rejected": (NotificationType.BOOKING_REJECTED, "Booking Rejected", "Your booking has been rejected"),
        "booking_paid": (NotificationType.BOOKING_PAID, "Payment Received", "Payment has been received for your booking"),
        "booking_delivered": (NotificationType.BOOKING_DELIVERED, "Content Delivered", "Content has been delivered for your booking"),
        "booking_completed": (NotificationType.BOOKING_COMPLETED, "Booking Completed", "Your booking has been completed"),
        "booking_cancelled": (NotificationType.BOOKING_CANCELLED, "Booking Cancelled", "Your booking has been cancelled"),
    }

    if event_type in notification_map:
        ntype, title, message = notification_map[event_type]
        service.create_notification(
            user_id=user_id,
            notification_type=ntype,
            title=title,
            message=message,
            data={"booking_id": booking_id}
        )


def create_payment_notification(db: Session, user_id: int, payment_id: int, booking_id: int, event_type: str):
    service = NotificationService(db)

    notification_map = {
        "payment_received": (NotificationType.PAYMENT_RECEIVED, "Payment Received", "Payment has been held in escrow"),
        "payment_released": (NotificationType.PAYMENT_RELEASED, "Payment Released", "Payment has been released to your account"),
        "payment_refunded": (NotificationType.PAYMENT_REFUNDED, "Payment Refunded", "Payment has been refunded"),
    }

    if event_type in notification_map:
        ntype, title, message = notification_map[event_type]
        service.create_notification(
            user_id=user_id,
            notification_type=ntype,
            title=title,
            message=message,
            data={"payment_id": payment_id, "booking_id": booking_id}
        )
