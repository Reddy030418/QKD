from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    api_title: str = "Quantum Key Distribution API"
    api_version: str = "1.0.0"
    api_description: str = "Backend API for BB84 Quantum Key Distribution simulation"

    # Database Settings
    database_url: str = "sqlite:///./qkd.db"

    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # QKD Settings
    default_key_length: int = 50
    default_noise_level: int = 5
    default_detector_efficiency: int = 95
    max_key_length: int = 500
    min_key_length: int = 10

    # WebSocket Settings
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 20

    # CORS Settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]

    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()
