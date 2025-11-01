"""
Rate limiting configuration and utilities using slowapi
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from redis import Redis
from loguru import logger

from app.core.config import settings


# Redis connection for rate limiting
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_user_tier_key(request: Request) -> str:
    """
    Custom key function that incorporates user tier for rate limiting
    Falls back to IP address for unauthenticated requests
    """
    # Check if user is authenticated and has tier info
    user = getattr(request.state, "user", None)
    
    if user and hasattr(user, "tier"):
        # Use user ID and tier for authenticated requests
        return f"user:{user.id}:{user.tier}"
    
    # Fall back to IP address for unauthenticated requests
    return f"ip:{get_remote_address(request)}"


# Initialize limiter with Redis storage
limiter = Limiter(
    key_func=get_user_tier_key,
    storage_uri=settings.REDIS_URL,
    strategy="fixed-window",
    default_limits=[],  # No default limits; specify per route
    headers_enabled=True,
)


def get_tier_limit(tier: str) -> str:
    """Get rate limit string for a given tier"""
    tier_limits = {
        "analyst": settings.RATE_LIMIT_FREE,
        "optimizer": settings.RATE_LIMIT_OPTIMIZER,
        "autopilot": settings.RATE_LIMIT_AUTOPILOT,
    }
    return tier_limits.get(tier, settings.RATE_LIMIT_FREE)


def tier_rate_limit(tier: str):
    """
    Decorator factory for tier-specific rate limiting
    Usage: @tier_rate_limit("optimizer")
    """
    limit_str = get_tier_limit(tier)
    return limiter.limit(limit_str)


# Rate limit decorators for common use cases
free_tier_limit = limiter.limit(settings.RATE_LIMIT_FREE)
optimizer_limit = limiter.limit(settings.RATE_LIMIT_OPTIMIZER)
autopilot_limit = limiter.limit(settings.RATE_LIMIT_AUTOPILOT)


def dynamic_tier_limit(request: Request) -> str:
    """
    Dynamic rate limit based on authenticated user's tier
    Returns the appropriate limit string
    """
    user = getattr(request.state, "user", None)
    
    if user and hasattr(user, "tier"):
        limit = get_tier_limit(user.tier)
        logger.debug(f"Rate limit for user {user.id} (tier: {user.tier}): {limit}")
        return limit
    
    # Default to free tier for unauthenticated users
    return settings.RATE_LIMIT_FREE


# Exemption patterns (health checks, webhooks, etc.)
RATE_LIMIT_EXEMPT_PATHS = [
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
]


def is_rate_limit_exempt(path: str) -> bool:
    """Check if a path is exempt from rate limiting"""
    return any(path.startswith(exempt) for exempt in RATE_LIMIT_EXEMPT_PATHS)
