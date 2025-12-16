"""
OAuth Provider Factory
Factory pattern for creating OAuth provider instances.
"""
from typing import Dict, Type
from oauth.base import BaseOAuthProvider, OAuthError
from oauth.tiktok import TikTokOAuthProvider
from oauth.youtube import YouTubeOAuthProvider
from oauth.instagram import InstagramOAuthProvider


# Registry of available OAuth providers
PROVIDERS: Dict[str, Type[BaseOAuthProvider]] = {
    "tiktok": TikTokOAuthProvider,
    "youtube": YouTubeOAuthProvider,
    "instagram": InstagramOAuthProvider
}


def get_oauth_provider(platform: str) -> BaseOAuthProvider:
    """
    Factory function to get the appropriate OAuth provider.
    
    Args:
        platform: Platform name (tiktok, youtube, instagram)
        
    Returns:
        Configured OAuth provider instance
        
    Raises:
        OAuthError: If platform is not supported
    """
    platform_lower = platform.lower()
    
    if platform_lower not in PROVIDERS:
        raise OAuthError(
            f"Unsupported platform: {platform}. Supported: {list(PROVIDERS.keys())}",
            platform,
            "UNSUPPORTED_PLATFORM"
        )
    
    provider_class = PROVIDERS[platform_lower]
    return provider_class()


def get_supported_platforms() -> list[str]:
    """Get list of supported OAuth platforms."""
    return list(PROVIDERS.keys())
