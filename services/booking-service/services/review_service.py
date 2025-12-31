from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from fastapi import HTTPException, status
from app.models.review import Review
from app.models.booking import Booking, BookingStatus
from app.schemas.review import ReviewCreate, UserRatingStats


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create_review(self, review_data: ReviewCreate, reviewer_id: int, reviewer_role: str) -> Review:
        booking = self.db.query(Booking).filter(
            Booking.id == review_data.booking_id,
            Booking.is_deleted == False
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.status != BookingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed bookings"
            )

        if reviewer_role == "business_owner":
            if booking.business_id != reviewer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only review your own bookings"
                )
            reviewed_id = booking.creator_id
        else:
            if booking.creator_id != reviewer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only review your own bookings"
                )
            reviewed_id = booking.business_id

        existing_review = self.db.query(Review).filter(
            Review.booking_id == review_data.booking_id,
            Review.reviewer_id == reviewer_id
        ).first()

        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this booking"
            )

        review = Review(
            booking_id=review_data.booking_id,
            reviewer_id=reviewer_id,
            reviewed_id=reviewed_id,
            reviewer_role=reviewer_role,
            rating=review_data.rating,
            comment=review_data.comment
        )

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_reviews_for_user(self, user_id: int) -> List[Review]:
        return self.db.query(Review).filter(Review.reviewed_id == user_id).all()

    def get_reviews_by_user(self, user_id: int) -> List[Review]:
        return self.db.query(Review).filter(Review.reviewer_id == user_id).all()

    def get_booking_reviews(self, booking_id: int) -> List[Review]:
        return self.db.query(Review).filter(Review.booking_id == booking_id).all()

    def get_user_rating_stats(self, user_id: int) -> UserRatingStats:
        reviews = self.db.query(Review).filter(Review.reviewed_id == user_id).all()

        if not reviews:
            return UserRatingStats(
                user_id=user_id,
                average_rating=0.0,
                total_reviews=0,
                rating_breakdown={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            )

        total = len(reviews)
        avg = sum(r.rating for r in reviews) / total

        breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in reviews:
            breakdown[r.rating] += 1

        return UserRatingStats(
            user_id=user_id,
            average_rating=round(avg, 2),
            total_reviews=total,
            rating_breakdown=breakdown
        )
