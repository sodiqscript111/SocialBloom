from urllib.parse import urlencode
from typing import Optional

from oauth.base import BaseOAuthProvider, OAuthTokenResponse, SocialProfile, OAuthError
from oauth.config import InstagramConfig


class InstagramOAuthProvider(BaseOAuthProvider):
    
    def __init__(self, config: Optional[InstagramConfig] = None):
        from oauth.config import get_instagram_config
        super().__init__(config or get_instagram_config())
    
    @property
    def platform_name(self) -> str:
        return "instagram"
    
    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "scope": ",".join(self.config.scopes),
            "redirect_uri": self.config.redirect_uri,
            "state": state
        }
        return f"{self.config.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        payload = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri
        }
        
        response = await self.http_client.post(
            self.config.token_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            raise OAuthError(
                f"Token exchange failed: {response.text}",
                self.platform_name,
                str(response.status_code)
            )
        
        data = response.json()
        
        if "error_message" in data:
            raise OAuthError(
                data.get("error_message"),
                self.platform_name,
                data.get("error_type")
            )
        
        short_lived_token = data["access_token"]
        return await self._exchange_for_long_lived_token(short_lived_token)
    
    async def _exchange_for_long_lived_token(self, short_lived_token: str) -> OAuthTokenResponse:
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": self.config.client_secret,
            "access_token": short_lived_token
        }
        
        response = await self.http_client.get(
            "https://graph.instagram.com/access_token",
            params=params
        )
        
        if response.status_code != 200:
            return OAuthTokenResponse(
                access_token=short_lived_token,
                expires_in=3600
            )
        
        data = response.json()
        
        return OAuthTokenResponse(
            access_token=data["access_token"],
            expires_in=data.get("expires_in", 5184000),
            token_type="Bearer"
        )
    
    async def get_user_profile(self, access_token: str) -> SocialProfile:
        params = {
            "fields": "id,username,account_type,media_count,followers_count,follows_count",
            "access_token": access_token
        }
        
        response = await self.http_client.get(
            self.config.user_info_url,
            params=params
        )
        
        if response.status_code != 200:
            raise OAuthError(
                f"Failed to fetch profile: {response.text}",
                self.platform_name,
                str(response.status_code)
            )
        
        data = response.json()
        
        if "error" in data:
            raise OAuthError(
                data["error"].get("message", "Unknown error"),
                self.platform_name,
                str(data["error"].get("code"))
            )
        
        return SocialProfile(
            platform_user_id=data.get("id", ""),
            username=data.get("username", ""),
            display_name=data.get("username", ""),
            profile_url=f"https://www.instagram.com/{data.get('username', '')}",
            avatar_url=None,
            follower_count=data.get("followers_count", 0),
            following_count=data.get("follows_count", 0),
            bio=None
        )
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": refresh_token
        }
        
        response = await self.http_client.get(
            "https://graph.instagram.com/refresh_access_token",
            params=params
        )
        
        if response.status_code != 200:
            raise OAuthError(
                f"Token refresh failed: {response.text}",
                self.platform_name,
                str(response.status_code)
            )
        
        data = response.json()
        
        return OAuthTokenResponse(
            access_token=data["access_token"],
            expires_in=data.get("expires_in", 5184000),
            token_type="Bearer"
        )
