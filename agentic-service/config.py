"""
Configuration management for agentic service.
Loads environment variables for database, OpenAI, Ollama, FAISS.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        case_sensitive=False,
    )

    database_url: Optional[str] = None
    openai_api_key: str
    ollama_base_url: str = "http://localhost:11434"
    faiss_index_path: str = "./data/faiss_index"
    hf_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Optional external APIs
    google_maps_api_key: Optional[str] = None
    amadeus_api_key: Optional[str] = None
    amadeus_api_secret: Optional[str] = None
    openweather_api_key: Optional[str] = None


settings = Settings()
