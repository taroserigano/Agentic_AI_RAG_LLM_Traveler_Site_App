"""
Configuration management for agentic service.
Loads environment variables for database, OpenAI, Ollama, FAISS.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Service configuration from environment variables."""
    
    database_url: str
    openai_api_key: str
    ollama_base_url: str = "http://localhost:11434"
    faiss_index_path: str = "./data/faiss_index"
    hf_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Optional external APIs
    google_maps_api_key: Optional[str] = None
    amadeus_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
