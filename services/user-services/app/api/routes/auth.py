"""
Authentication Routes
Handles token refresh and authentication-related endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import Token, TokenRefresh
from db.database import get_db
from utils.jwt_handler import verify_token, create_token_pair

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/refresh", response_model=Token)
async def refresh_token(token_request: TokenRefresh):
    """
    Refresh access token using a valid refresh token.
    
    Args:
        token_request: Contains the refresh token
        
    Returns:
        New access and refresh token pair
    """
    payload = verify_token(token_request.refresh_token, expected_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new token pair
    return create_token_pair(
        user_id=payload["user_id"],
        email=payload["email"],
        role=payload["role"]
    )
