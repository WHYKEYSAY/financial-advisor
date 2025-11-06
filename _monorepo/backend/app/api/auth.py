"""
Authentication API endpoints
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from loguru import logger

from app.core.db import get_db
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_token,
    hash_token
)
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.models import User, RefreshToken, Quota
from app.schemas.auth import (
    UserRegister, 
    UserLogin, 
    TokenResponse, 
    UserResponse,
    RefreshTokenRequest
)


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        locale=user_data.locale,
        tier="analyst",  # Default to free tier
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create quota for new user (analyst tier = 5 statements/month)
    quota = Quota(
        user_id=user.id,
        period_start=datetime.utcnow(),
        period_end=datetime.utcnow() + timedelta(days=30),
        statements_parsed=0,
        statements_limit=5,  # Analyst tier: 5 statements per month
        ai_calls_used=0,
        ai_calls_limit=settings.AI_QUOTA_FREE
    )
    db.add(quota)
    db.commit()
    
    logger.info(f"New user registered: {user.email} (ID: {user.id})")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        locale=user.locale,
        tier=user.tier,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin, 
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    Returns JWT tokens and sets HTTPOnly cookies
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "tier": user.tier})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in database (hashed)
    refresh_token_hash = hash_token(refresh_token)
    expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=expires_at,
        revoked=False
    )
    db.add(db_refresh_token)
    db.commit()
    
    # Set HTTPOnly cookies for web clients
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.JWT_ACCESS_TTL_MIN * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60
    )
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_data: RefreshTokenRequest = None,
    refresh_token_cookie: str = Cookie(default=None, alias="refresh_token")
):
    """
    Refresh access token using refresh token
    Supports both body and cookie-based refresh tokens
    """
    # Get refresh token from body or cookie
    refresh_token = None
    if refresh_data and refresh_data.refresh_token:
        refresh_token = refresh_data.refresh_token
    elif refresh_token_cookie:
        refresh_token = refresh_token_cookie
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    
    # Check if refresh token exists and is valid
    refresh_token_hash = hash_token(refresh_token)
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == refresh_token_hash,
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Revoke old refresh token
    db_token.revoked = True
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": str(user.id), "tier": user.tier})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store new refresh token
    new_refresh_token_hash = hash_token(new_refresh_token)
    new_expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_token_hash,
        expires_at=new_expires_at,
        revoked=False
    )
    db.add(new_db_token)
    db.commit()
    
    # Update cookies
    if response:
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            max_age=settings.JWT_ACCESS_TTL_MIN * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            max_age=settings.JWT_REFRESH_TTL_DAYS * 24 * 60 * 60
        )
    
    logger.info(f"Token refreshed for user: {user.email} (ID: {user.id})")
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
def logout(
    refresh_token_cookie: str = Cookie(default=None, alias="refresh_token"),
    response: Response = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token and clearing cookies
    """
    # Revoke refresh token if provided
    if refresh_token_cookie:
        refresh_token_hash = hash_token(refresh_token_cookie)
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == refresh_token_hash,
            RefreshToken.user_id == current_user.id
        ).first()
        
        if db_token:
            db_token.revoked = True
            db.commit()
    
    # Clear cookies
    if response:
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
    
    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user info
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        locale=current_user.locale,
        tier=current_user.tier,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )
