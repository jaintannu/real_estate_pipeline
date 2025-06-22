from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql://username:password@localhost:5432/real_estate_db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "real_estate_db"
    database_user: str = "username"
    database_password: str = "password"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # API Keys
    rentspider_api_key: Optional[str] = None
    rentcast_api_key: Optional[str] = None
    zillow_api_key: Optional[str] = None
    walkscore_api_key: Optional[str] = None
    
    # Application settings
    secret_key: str = "your-super-secret-key-here"
    debug: bool = True
    log_level: str = "INFO"
    api_v1_str: str = "/api/v1"
    
    # Rate limiting
    default_rate_limit: int = 100
    api_rate_limit_per_minute: int = 60
    
    # Celery settings
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    # Data collection settings
    default_city: str = "San Francisco"
    default_state: str = "CA"
    batch_size: int = 100
    max_retries: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()