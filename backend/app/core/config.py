"""
Application configuration using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    TZ: str = "UTC"
    
    # Security
    SECRET_KEY: str
    JWT_ALG: str = "HS256"
    JWT_ACCESS_TTL_MIN: int = 10080  # 7 days (7 * 24 * 60)
    JWT_REFRESH_TTL_DAYS: int = 14
    ENCRYPTION_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # URLs
    BACKEND_URL: str
    FRONTEND_URL: str
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Stripe
    STRIPE_PUBLIC_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    STRIPE_PRICE_ANALYST: str = "price_free"
    STRIPE_PRICE_OPTIMIZER_MONTHLY: str = ""
    STRIPE_PRICE_OPTIMIZER_YEARLY: str = ""
    STRIPE_PRICE_AUTOPILOT_MONTHLY: str = ""
    STRIPE_PRICE_AUTOPILOT_YEARLY: str = ""
    
    # Plaid
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"
    
    # File Storage
    FILE_STORAGE_DIR: str = "/data/uploads"
    MAX_FILE_SIZE_MB: int = 25
    
    # Rate Limiting
    RATE_LIMIT_FREE: str = "60/minute"
    RATE_LIMIT_OPTIMIZER: str = "240/minute"
    RATE_LIMIT_AUTOPILOT: str = "600/minute"
    
    # AI Quotas
    AI_QUOTA_FREE: int = 100
    AI_QUOTA_OPTIMIZER: int = 1000
    AI_QUOTA_AUTOPILOT: int = 3000
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
