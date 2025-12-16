from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import httpx


@dataclass
class OAuthTokenResponse:
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None


@dataclass
class SocialProfile:
    platform_user_id: str
    username: str
    display_name: str
    profile_url: str
    avatar_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    bio: Optional[str] = None


class BaseOAuthProvider(ABC):
    
    def __init__(self, config):
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        pass
    
    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        pass
    
    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        pass
    
    @abstractmethod
    async def get_user_profile(self, access_token: str) -> SocialProfile:
        pass
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        raise NotImplementedError(f"{self.platform_name} does not support token refresh")
    
    async def close(self):
        await self.http_client.aclose()


class OAuthError(Exception):
    
    def __init__(self, message: str, platform: str, error_code: Optional[str] = None):
        self.message = message
        self.platform = platform
        self.error_code = error_code
        super().__init__(f"[{platform}] {message}")
