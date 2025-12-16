from urllib.parse import urlencode
from typing import Optional

from oauth.base import BaseOAuthProvider, OAuthTokenResponse, SocialProfile, OAuthError
from oauth.config import YouTubeConfig


class YouTubeOAuthProvider(BaseOAuthProvider):
    
    def __init__(self, config: Optional[YouTubeConfig] = None):
        from oauth.config import get_youtube_config
        super().__init__(config or get_youtube_config())
    
    @property
    def platform_name(self) -> str:
        return "youtube"
    
    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.config.client_id,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "redirect_uri": self.config.redirect_uri,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
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
            "part": "snippet,statistics",
            "mine": "true"
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
        
        if "error" in data:
            raise OAuthError(
                data["error"].get("message", "Unknown error"),
                self.platform_name,
                str(data["error"].get("code"))
            )
        
        items = data.get("items", [])
        if not items:
            raise OAuthError(
                "No YouTube channel found for this account",
                self.platform_name,
                "NO_CHANNEL"
            )
        
        channel = items[0]
        snippet = channel.get("snippet", {})
        statistics = channel.get("statistics", {})
        
        return SocialProfile(
            platform_user_id=channel.get("id", ""),
            username=snippet.get("customUrl", "").replace("@", ""),
            display_name=snippet.get("title", ""),
            profile_url=f"https://www.youtube.com/channel/{channel.get('id', '')}",
            avatar_url=snippet.get("thumbnails", {}).get("default", {}).get("url"),
            follower_count=int(statistics.get("subscriberCount", 0)),
            following_count=0,
            bio=snippet.get("description")
        )
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        payload = {
            "client_id": self.config.client_id,
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
            refresh_token=refresh_token,
            expires_in=data.get("expires_in"),
            token_type=data.get("token_type", "Bearer")
        )
