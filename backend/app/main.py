"""
CreditSphere API - Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from loguru import logger
import sys

from app.core import settings
from app.core.rate_limit import limiter
from app.api import auth, quota

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL
)

# Create FastAPI app
app = FastAPI(
    title="CreditSphere API",
    description="Your AI Financial Co-Pilot | 您的 AI 金融管家",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if settings.APP_ENV == "development" else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(quota.router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting CreditSphere API in {settings.APP_ENV} mode")
    logger.info(f"Allowed CORS origins: {settings.cors_origins}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down CreditSphere API")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "CreditSphere API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}
