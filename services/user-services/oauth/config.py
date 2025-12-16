"""
OAuth Configuration Module
Centralized configuration for all OAuth providers.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OAuthConfig:
    """Base configuration for OAuth providers."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]


@dataclass
class TikTokConfig(OAuthConfig):
    """TikTok-specific OAuth configuration."""
    auth_url: str = "https://www.tiktok.com/v2/auth/authorize/"
    token_url: str = "https://open.tiktokapis.com/v2/oauth/token/"
    user_info_url: str = "https://open.tiktokapis.com/v2/user/info/"


@dataclass
class YouTubeConfig(OAuthConfig):
    """YouTube/Google-specific OAuth configuration."""
    auth_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url: str = "https://oauth2.googleapis.com/token"
    user_info_url: str = "https://www.googleapis.com/youtube/v3/channels"


@dataclass
class InstagramConfig(OAuthConfig):
    """Instagram-specific OAuth configuration."""
    auth_url: str = "https://www.instagram.com/oauth/authorize"
    token_url: str = "https://api.instagram.com/oauth/access_token"
    user_info_url: str = "https://graph.instagram.com/me"


# Base redirect URI - adjust for your deployment
BASE_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_BASE", "http://127.0.0.1:8000/social/callback")


def get_tiktok_config() -> TikTokConfig:
    """Get TikTok OAuth configuration."""
    return TikTokConfig(
        client_id=os.getenv("TIKTOK_CLIENT_KEY", "awb4wwd59ue93uyp"),
        client_secret=os.getenv("TIKTOK_CLIENT_SECRET", "2tc5H7IS90FnQ3RhGEwreelijG6M6vmZ"),
        redirect_uri=f"{BASE_REDIRECT_URI}/tiktok",
        scopes=["user.info.basic", "user.info.profile", "user.info.stats"]
    )


def get_youtube_config() -> YouTubeConfig:
    """Get YouTube/Google OAuth configuration."""
    return YouTubeConfig(
        client_id=os.getenv(
            "YOUTUBE_CLIENT_ID",
            "1055231814715-mkfdshbi2l4rkmvn39l4f530o61o6c4u.apps.googleusercontent.com"
        ),
        client_secret=os.getenv(
            "YOUTUBE_CLIENT_SECRET",
            "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"
        ),
        redirect_uri=f"{BASE_REDIRECT_URI}/youtube",
        scopes=[
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    )


def get_instagram_config() -> InstagramConfig:
    """Get Instagram OAuth configuration."""
    return InstagramConfig(
        client_id=os.getenv("INSTAGRAM_APP_ID", "YOUR_INSTAGRAM_APP_ID"),
        client_secret=os.getenv("INSTAGRAM_APP_SECRET", "YOUR_INSTAGRAM_APP_SECRET"),
        redirect_uri=f"{BASE_REDIRECT_URI}/instagram",
        scopes=["instagram_business_basic", "instagram_business_manage_insights"]
    )
