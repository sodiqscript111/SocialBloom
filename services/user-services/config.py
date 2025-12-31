import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:password@localhost/testing"
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    kafka_bootstrap_servers: str = "localhost:9092"
    instagram_client_id: str = ""
    instagram_client_secret: str = ""
    tiktok_client_id: str = ""
    tiktok_client_secret: str = ""
    youtube_client_id: str = ""
    youtube_client_secret: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
