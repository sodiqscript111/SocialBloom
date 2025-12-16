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

_oauth_states: dict = {}


def get_social_service(db: Session = Depends(get_db)) -> SocialConnectionService:
    return SocialConnectionService(db)


@router.get("/platforms")
async def list_supported_platforms():
    return {
        "platforms": get_supported_platforms(),
        "message": "Use GET /social/connect/{platform} to start OAuth flow"
    }


@router.get("/connections", response_model=List[SocialConnectionResponse])
async def get_my_connections(
    current_user: TokenData = Depends(get_current_user),
    service: SocialConnectionService = Depends(get_social_service)
):
    return service.get_user_connections(current_user.user_id)


@router.get("/connect/{platform}")
async def start_oauth_flow(
    platform: str,
    current_user: TokenData = Depends(get_current_user)
):
    try:
        provider = get_oauth_provider(platform)
        
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
        
        tokens = await provider.exchange_code_for_token(code)
        
        profile = await provider.get_user_profile(tokens.access_token)
        
        await provider.close()
        
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
