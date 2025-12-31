from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from app.schemas.review import ReviewCreate, ReviewResponse, UserRatingStats
from services.review_service import ReviewService
from auth.dependencies import get_current_user, TokenData


router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(db)


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.create_review(review, current_user.user_id, current_user.role)


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(
    user_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.get_reviews_for_user(user_id)


@router.get("/user/{user_id}/stats", response_model=UserRatingStats)
async def get_user_rating_stats(
    user_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.get_user_rating_stats(user_id)


@router.get("/my/given", response_model=List[ReviewResponse])
async def get_my_given_reviews(
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.get_reviews_by_user(current_user.user_id)


@router.get("/my/received", response_model=List[ReviewResponse])
async def get_my_received_reviews(
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.get_reviews_for_user(current_user.user_id)


@router.get("/booking/{booking_id}", response_model=List[ReviewResponse])
async def get_booking_reviews(
    booking_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service)
):
    return service.get_booking_reviews(booking_id)
