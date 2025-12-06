"""
Lambda-specific configuration - minimal dependencies.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service configuration from environment variables."""

    model_config = SettingsConfigDict(
        extra="allow",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    openai_api_key: str
    
    # Optional external APIs
    google_maps_api_key: Optional[str] = None
    amadeus_api_key: Optional[str] = None
    amadeus_api_secret: Optional[str] = None
    openweather_api_key: Optional[str] = None


settings = Settings()
