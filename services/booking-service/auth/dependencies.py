"""
Authentication Dependencies for Booking Service
Provides FastAPI dependencies for JWT-based authentication.
"""
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from auth.jwt_handler import verify_token


# OAuth2 scheme - points to User Service login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/login")


class TokenData(BaseModel):
    """Data extracted from a valid JWT token."""
    user_id: int
    email: str
    role: str


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    FastAPI dependency that extracts and validates the current user from JWT.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException 401 if token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token, expected_type="access")
    
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("user_id")
    email = payload.get("email")
    role = payload.get("role")
    
    if user_id is None or email is None or role is None:
        raise credentials_exception
    
    return TokenData(user_id=user_id, email=email, role=role)


def require_roles(allowed_roles: List[str]):
    """
    Factory function that creates a dependency to check user roles.
    
    Args:
        allowed_roles: List of roles that are allowed to access the endpoint
        
    Returns:
        A dependency function that validates the user's role
    """
    async def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    
    return role_checker


# Convenience dependencies
require_business_owner = require_roles(["business_owner"])
require_creator = require_roles(["creator"])
