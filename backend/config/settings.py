"""
CrickPredict Configuration - Single Source of Truth
All environment variables and app settings are managed here.
Following 12-Factor App methodology.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Application Settings with validation.
    All settings come from environment variables.
    No hardcoded defaults for critical values - fail fast if missing.
    """
    
    # App Info
    APP_NAME: str = "CrickPredict"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    
    # MongoDB Configuration
    MONGO_URL: str = Field(..., description="MongoDB connection string")
    DB_NAME: str = Field(..., description="Database name")
    MONGO_MIN_POOL_SIZE: int = Field(default=10)
    MONGO_MAX_POOL_SIZE: int = Field(default=100)
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = Field(default=50)
    REDIS_DECODE_RESPONSES: bool = Field(default=True)
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(default="*")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="crickpredict-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)  # 7 days
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30)
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60)
    
    # Game Configuration
    SIGNUP_BONUS_COINS: int = Field(default=10000)
    DAILY_REWARD_BASE: int = Field(default=500)
    DAILY_REWARD_INCREMENT: int = Field(default=100)
    DAILY_REWARD_MAX_STREAK: int = Field(default=7)
    DAILY_STREAK_BONUS: int = Field(default=200)
    
    # Cricbuzz Scraper Configuration
    CRICBUZZ_BASE_URL: str = Field(default="https://www.cricbuzz.com")
    SCRAPER_REQUEST_TIMEOUT: int = Field(default=10)
    SCRAPER_RETRY_ATTEMPTS: int = Field(default=3)
    SCORE_UPDATE_INTERVAL_SECONDS: int = Field(default=5)
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        return v
    
    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins string to list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Settings are loaded once and cached for performance.
    """
    return Settings()


# Export singleton instance
settings = get_settings()
