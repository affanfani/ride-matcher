from functools import lru_cache
from pydantic_settings import BaseSettings
from app import env_config

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = env_config.DATABASE_URL
    
    # Application Configuration
    app_name: str = "Ride Matcher API"
    app_version: str = "1.0.0"
    debug: bool = env_config.DEBUG
    
    # Security Configuration (for optional JWT)
    secret_key: str = env_config.SECRET_KEY
    access_token_expire_minutes: int = env_config.ACCESS_TOKEN_EXPIRE_MINUTES
    algorithm: str = env_config.ALGORITHM
    
    # Environment
    environment: str = env_config.ENVIRONMENT

@lru_cache
def get_settings() -> Settings:
    return Settings()