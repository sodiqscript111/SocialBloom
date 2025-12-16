"""
Base OAuth Provider
Abstract base class that all OAuth providers must implement.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import httpx


@dataclass
class OAuthTokenResponse:
    """Standardized token response from OAuth providers."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None


@dataclass
class SocialProfile:
    """Standardized user profile data from social platforms."""
    platform_user_id: str
    username: str
    display_name: str
    profile_url: str
    avatar_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    bio: Optional[str] = None


class BaseOAuthProvider(ABC):
    """
    Abstract base class for OAuth providers.
    
    All platform-specific providers must implement these methods
    to ensure consistent behavior across the application.
    """
    
    def __init__(self, config):
        """
        Initialize the provider with configuration.
        
        Args:
            config: Platform-specific OAuthConfig instance
        """
        self.config = config
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform identifier (e.g., 'tiktok', 'youtube')."""
        pass
    
    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """
        Generate the OAuth authorization URL.
        
        Args:
            state: CSRF protection state token
            
        Returns:
            Full authorization URL to redirect user to
        """
        pass
    
    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> OAuthTokenResponse:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            OAuthTokenResponse with tokens
            
        Raises:
            OAuthError: If token exchange fails
        """
        pass
    
    @abstractmethod
    async def get_user_profile(self, access_token: str) -> SocialProfile:
        """
        Fetch user profile data from the platform.
        
        Args:
            access_token: Valid access token
            
        Returns:
            SocialProfile with user data
            
        Raises:
            OAuthError: If profile fetch fails
        """
        pass
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenResponse:
        """
        Refresh an expired access token.
        
        Default implementation - override if platform has different flow.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            OAuthTokenResponse with new tokens
        """
        raise NotImplementedError(f"{self.platform_name} does not support token refresh")
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()


class OAuthError(Exception):
    """Custom exception for OAuth-related errors."""
    
    def __init__(self, message: str, platform: str, error_code: Optional[str] = None):
        self.message = message
        self.platform = platform
        self.error_code = error_code
        super().__init__(f"[{platform}] {message}")
