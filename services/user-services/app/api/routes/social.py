"""
Social Connection Routes
API endpoints for managing social platform connections via OAuth.
"""
import secrets
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.schemas.user import SocialConnectionResponse
from db.database import get_db
from services.social_service import SocialConnectionService
from utils.auth_dependencies import get_current_user, TokenData
from oauth.factory import get_oauth_provider, get_supported_platforms
from oauth.base import OAuthError


router = APIRouter(prefix="/social", tags=["Social Connections"])

# In-memory state storage (use Redis in production)
_oauth_states: dict = {}


def get_social_service(db: Session = Depends(get_db)) -> SocialConnectionService:
    return SocialConnectionService(db)


# --- Public Endpoints ---

@router.get("/platforms")
async def list_supported_platforms():
    """
    List all supported social platforms for OAuth connection.
    
    Returns:
        List of platform names that can be connected
    """
    return {
        "platforms": get_supported_platforms(),
        "message": "Use GET /social/connect/{platform} to start OAuth flow"
    }


# --- Protected Endpoints (Require Authentication) ---

@router.get("/connections", response_model=List[SocialConnectionResponse])
async def get_my_connections(
    current_user: TokenData = Depends(get_current_user),
    service: SocialConnectionService = Depends(get_social_service)
):
    """
    Get all social connections for the authenticated user.
    
    Returns:
        List of connected social platforms
    """
    return service.get_user_connections(current_user.user_id)


@router.get("/connect/{platform}")
async def start_oauth_flow(
    platform: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Start OAuth flow for a social platform.
    
    Args:
        platform: Platform to connect (tiktok, youtube, instagram)
        
    Returns:
        OAuth authorization URL to redirect user to
    """
    try:
        provider = get_oauth_provider(platform)
        
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        _oauth_states[state] = {
            "user_id": current_user.user_id,
            "platform": platform
        }
        
        auth_url = provider.get_authorization_url(state)
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "message": "Redirect user to authorization_url to complete OAuth"
        }
        
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/callback/{platform}")
async def oauth_callback(
    platform: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State token for CSRF protection"),
    service: SocialConnectionService = Depends(get_social_service)
):
    """
    Handle OAuth callback from social platform.
    
    This endpoint is called by the OAuth provider after user authorizes.
    It exchanges the code for tokens and saves the connection.
    
    Args:
        platform: Platform that sent the callback
        code: Authorization code
        state: State token for verification
        
    Returns:
        Connection details or redirect to frontend
    """
    # Verify state token
    state_data = _oauth_states.pop(state, None)
    
    if not state_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token"
        )
    
    if state_data["platform"] != platform:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Platform mismatch in state token"
        )
    
    try:
        provider = get_oauth_provider(platform)
        
        # Exchange code for tokens
        tokens = await provider.exchange_code_for_token(code)
        
        # Get user profile
        profile = await provider.get_user_profile(tokens.access_token)
        
        await provider.close()
        
        # Save connection to database
        connection = await service.create_or_update_connection(
            user_id=state_data["user_id"],
            platform=platform,
            tokens=tokens,
            profile=profile
        )
        
        return {
            "success": True,
            "message": f"Successfully connected {platform}",
            "connection": {
                "id": connection.id,
                "platform": platform,
                "username": connection.platform_username,
                "follower_count": connection.follower_count
            }
        }
        
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/connections/{connection_id}")
async def disconnect_platform(
    connection_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: SocialConnectionService = Depends(get_social_service)
):
    """
    Disconnect a social platform.
    
    Args:
        connection_id: ID of the connection to remove
        
    Returns:
        Success message
    """
    deleted = service.delete_connection(current_user.user_id, connection_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    return {"success": True, "message": "Platform disconnected successfully"}


@router.post("/connections/{platform}/refresh")
async def refresh_platform_token(
    platform: str,
    current_user: TokenData = Depends(get_current_user),
    service: SocialConnectionService = Depends(get_social_service)
):
    """
    Refresh access token for a connected platform.
    
    Args:
        platform: Platform to refresh token for
        
    Returns:
        Updated connection details
    """
    connection = await service.refresh_connection_token(
        current_user.user_id, 
        platform
    )
    
    return {
        "success": True,
        "message": f"Token refreshed for {platform}",
        "expires_at": connection.token_expires_at.isoformat() if connection.token_expires_at else None
    }


@router.post("/connections/{platform}/sync")
async def sync_platform_profile(
    platform: str,
    current_user: TokenData = Depends(get_current_user),
    service: SocialConnectionService = Depends(get_social_service)
):
    """
    Sync profile data (follower count, etc.) from a connected platform.
    
    Args:
        platform: Platform to sync profile from
        
    Returns:
        Updated connection details
    """
    connection = await service.sync_connection_profile(
        current_user.user_id,
        platform
    )
    
    return {
        "success": True,
        "message": f"Profile synced for {platform}",
        "follower_count": connection.follower_count,
        "username": connection.platform_username
    }
