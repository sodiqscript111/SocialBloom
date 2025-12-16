from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import SocialConnection, SocialPlatform, User
from oauth.factory import get_oauth_provider
from oauth.base import OAuthError, SocialProfile, OAuthTokenResponse


class SocialConnectionService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_connections(self, user_id: int) -> List[SocialConnection]:
        return self.db.query(SocialConnection).filter(
            SocialConnection.user_id == user_id
        ).all()
    
    def get_connection_by_platform(
        self, 
        user_id: int, 
        platform: str
    ) -> Optional[SocialConnection]:
        return self.db.query(SocialConnection).filter(
            SocialConnection.user_id == user_id,
            SocialConnection.platform == platform
        ).first()
    
    async def create_or_update_connection(
        self,
        user_id: int,
        platform: str,
        tokens: OAuthTokenResponse,
        profile: SocialProfile
    ) -> SocialConnection:
        existing = self.get_connection_by_platform(user_id, platform)
        
        expires_at = None
        if tokens.expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=tokens.expires_in)
        
        if existing:
            existing.platform_user_id = profile.platform_user_id
            existing.platform_username = profile.username
            existing.display_name = profile.display_name
            existing.profile_url = profile.profile_url
            existing.avatar_url = profile.avatar_url
            existing.follower_count = profile.follower_count
            existing.access_token = tokens.access_token
            existing.refresh_token = tokens.refresh_token
            existing.token_expires_at = expires_at
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        new_connection = SocialConnection(
            user_id=user_id,
            platform=SocialPlatform(platform),
            platform_user_id=profile.platform_user_id,
            platform_username=profile.username,
            display_name=profile.display_name,
            profile_url=profile.profile_url,
            avatar_url=profile.avatar_url,
            follower_count=profile.follower_count,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_expires_at=expires_at
        )
        
        self.db.add(new_connection)
        self.db.commit()
        self.db.refresh(new_connection)
        return new_connection
    
    def delete_connection(self, user_id: int, connection_id: int) -> bool:
        connection = self.db.query(SocialConnection).filter(
            SocialConnection.id == connection_id
        ).first()
        
        if not connection:
            return False
        
        if connection.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this connection"
            )
        
        self.db.delete(connection)
        self.db.commit()
        return True
    
    async def refresh_connection_token(
        self, 
        user_id: int, 
        platform: str
    ) -> SocialConnection:
        connection = self.get_connection_by_platform(user_id, platform)
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {platform} connection found"
            )
        
        if not connection.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{platform} connection does not support token refresh"
            )
        
        try:
            provider = get_oauth_provider(platform)
            new_tokens = await provider.refresh_access_token(connection.refresh_token)
            await provider.close()
            
            connection.access_token = new_tokens.access_token
            if new_tokens.refresh_token:
                connection.refresh_token = new_tokens.refresh_token
            if new_tokens.expires_in:
                connection.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=new_tokens.expires_in
                )
            
            self.db.commit()
            self.db.refresh(connection)
            return connection
            
        except OAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def sync_connection_profile(
        self, 
        user_id: int, 
        platform: str
    ) -> SocialConnection:
        connection = self.get_connection_by_platform(user_id, platform)
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {platform} connection found"
            )
        
        try:
            provider = get_oauth_provider(platform)
            profile = await provider.get_user_profile(connection.access_token)
            await provider.close()
            
            connection.platform_username = profile.username
            connection.display_name = profile.display_name
            connection.follower_count = profile.follower_count
            connection.avatar_url = profile.avatar_url
            
            self.db.commit()
            self.db.refresh(connection)
            return connection
            
        except OAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
