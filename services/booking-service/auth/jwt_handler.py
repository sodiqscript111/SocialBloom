"""
JWT Handler Module for Booking Service
Provides functions for verifying JWT tokens (shared secret with User Service).
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# Configuration - MUST match User Service
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


def verify_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token string
        expected_type: Expected token type ('access' or 'refresh')
        
    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != expected_type:
            return None
            
        return payload
    except JWTError:
        return None
