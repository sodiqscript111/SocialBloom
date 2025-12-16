from urllib.parse import urlencode
from typing import Optional

from oauth.base import BaseOAuthProvider, OAuthTokenResponse, SocialProfile, OAuthError
from oauth.config import TikTokConfig


class TikTokOAuthProvider(BaseOAuthProvider):
    
    def __init__(self, config: Optional[TikTokConfig] = None):
        from oauth.config import get_tiktok_config
        super().__init__(config or get_tiktok_config())
    
    @property
    def platform_name(self) -> str:
        return "tiktok"
    
    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_key": self.config.client_id,
            "response_type": "code",
            "scope": ",".join(self.config.scopes),
            "redirect_uri": self.config.redirect_uri,
            "state": state
        }
        return f"{self.config.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        payload = {
            "client_key": self.config.client_id,
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
        
        if "error" in data:
            raise OAuthError(
                data.get("error_description", data["error"]),
                self.platform_name,
                data.get("error")
            )
        
        return OAuthTokenResponse(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            token_type=data.get("token_type", "Bearer"),
            scope=data.get("scope")
        )
    
    async def get_user_profile(self, access_token: str) -> SocialProfile:
        params = {
            "fields": "open_id,union_id,avatar_url,display_name,username,follower_count,following_count,bio_description"
        }
        
        response = await self.http_client.get(
            self.config.user_info_url,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            raise OAuthError(
                f"Failed to fetch profile: {response.text}",
                self.platform_name,
                str(response.status_code)
            )
        
        data = response.json()
        
        if data.get("error", {}).get("code"):
            raise OAuthError(
                data["error"].get("message", "Unknown error"),
                self.platform_name,
                data["error"].get("code")
            )
        
        user_data = data.get("data", {}).get("user", {})
        
        return SocialProfile(
            platform_user_id=user_data.get("open_id", ""),
            username=user_data.get("username", ""),
            display_name=user_data.get("display_name", ""),
            profile_url=f"https://www.tiktok.com/@{user_data.get('username', '')}",
            avatar_url=user_data.get("avatar_url"),
            follower_count=user_data.get("follower_count", 0),
            following_count=user_data.get("following_count", 0),
            bio=user_data.get("bio_description")
        )
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        payload = {
            "client_key": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = await self.http_client.post(
            self.config.token_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
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
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            token_type=data.get("token_type", "Bearer")
        )
