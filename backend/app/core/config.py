from pydantic import BaseSettings, validator
from typing import List
import os
import json

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
    allowed_origins: List[str] = []

    # Runtime/Environment
    app_env: str = "development"

    # Rate Limiting (optional)
    rate_limit_enabled: bool = True
    auth_rate_limit_requests: int = 20
    auth_rate_limit_window_seconds: int = 60
    simulation_rate_limit_requests: int = 10
    simulation_rate_limit_window_seconds: int = 60
    seed_dev_admin: bool = True
    initial_admin_username: str = "admin"
    initial_admin_email: str = "admin@local.dev"
    initial_admin_password: str = "Admin1234"

    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "json"

    @validator("database_url")
    def validate_database_url(cls, value: str) -> str:
        if not value or "://" not in value:
            raise ValueError("DATABASE_URL must be a valid URL-like connection string")
        # Normalize SQLite relative URLs so runtime cwd changes don't switch databases.
        if value.startswith("sqlite:///./"):
            backend_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            )  # .../backend
            project_root = os.path.dirname(backend_dir)
            relative_path = value.replace("sqlite:///./", "", 1)
            absolute_path = os.path.abspath(os.path.join(project_root, relative_path))
            return f"sqlite:///{absolute_path.replace(os.sep, '/')}"
        return value

    @validator("secret_key")
    def validate_secret_key(cls, value: str) -> str:
        if len(value or "") < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value

    @validator("algorithm")
    def validate_algorithm(cls, value: str) -> str:
        allowed = {"HS256", "HS384", "HS512"}
        if value not in allowed:
            raise ValueError(f"ALGORITHM must be one of {sorted(allowed)}")
        return value

    @validator("access_token_expire_minutes")
    def validate_access_token_expiry(cls, value: int) -> int:
        if value < 5 or value > 1440:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 5 and 1440")
        return value

    @validator("allowed_origins", pre=True)
    def parse_allowed_origins(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []
            if text.startswith("["):
                parsed = json.loads(text)
                if not isinstance(parsed, list):
                    raise ValueError("ALLOWED_ORIGINS JSON must be a list")
                return [str(item).strip() for item in parsed if str(item).strip()]
            return [part.strip() for part in text.split(",") if part.strip()]
        raise ValueError("ALLOWED_ORIGINS must be a list or comma-separated string")

    @validator("app_env")
    def validate_app_env(cls, value: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        normalized = (value or "").strip().lower()
        if normalized not in allowed:
            raise ValueError(f"APP_ENV must be one of {sorted(allowed)}")
        return normalized

    @validator("allowed_origins")
    def validate_allowed_origins(cls, value: List[str], values):
        app_env = values.get("app_env", "development")
        if app_env in {"production", "staging"} and not value:
            raise ValueError("ALLOWED_ORIGINS cannot be empty in production/staging")
        return value

    @validator(
        "auth_rate_limit_requests",
        "auth_rate_limit_window_seconds",
        "simulation_rate_limit_requests",
        "simulation_rate_limit_window_seconds",
    )
    def validate_rate_limit_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Rate limit values must be positive integers")
        return value

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        case_sensitive = False

# Create global settings instance
settings = Settings()
