"""
Configuration management using environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path
from typing import List, Union


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./meetings.db"
    
    # File Upload
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 100
    
    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    
    # Whisper
    whisper_model: str = "base"
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # CORS - can be comma-separated string or list
    cors_origins: Union[List[str], str] = "http://localhost:5173,http://localhost:3000"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated string into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
