from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from app.schemas.notification import NotificationResponse, NotificationList, MarkReadRequest
from services.notification_service import NotificationService
from auth.dependencies import get_current_user, TokenData


router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("", response_model=NotificationList)
async def get_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    return service.get_user_notifications(current_user.user_id, unread_only, limit)


@router.get("/unread/count")
async def get_unread_count(
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    count = service.get_unread_count(current_user.user_id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    return service.mark_as_read(notification_id, current_user.user_id)


@router.post("/read-multiple")
async def mark_multiple_read(
    request: MarkReadRequest,
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    count = service.mark_multiple_as_read(request.notification_ids, current_user.user_id)
    return {"marked_count": count}


@router.post("/read-all")
async def mark_all_read(
    current_user: TokenData = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    count = service.mark_all_as_read(current_user.user_id)
    return {"marked_count": count}
