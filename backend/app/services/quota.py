"""
Quota tracking service for AI calls and rate limits
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.models import User, Quota
from app.core.config import settings


class QuotaExceeded(Exception):
    """Exception raised when quota is exceeded"""
    def __init__(self, message: str, upgrade_tier: str):
        self.message = message
        self.upgrade_tier = upgrade_tier
        super().__init__(self.message)


class QuotaService:
    """Service for managing user quotas"""
    
    # Statement-based quotas (primary)
    STATEMENT_QUOTAS = {
        "analyst": 5,        # 5 statements/month free
        "optimizer": 50,     # 50 statements/month
        "autopilot": 999999, # Unlimited
    }
    
    # AI call quotas (fallback for unknown merchants)
    TIER_QUOTAS = {
        "analyst": settings.AI_QUOTA_FREE,
        "optimizer": settings.AI_QUOTA_OPTIMIZER,
        "autopilot": settings.AI_QUOTA_AUTOPILOT,
    }
    
    UPGRADE_PROMPTS = {
        "analyst": {
            "en": "🚀 You've used all 5 free statements this month. Upgrade to Optimizer for 50 statements/month!",
            "zh": "🚀 您已用完本月 5 份免费账单额度。升级至 Optimizer 可获得每月 50 份账单！"
        },
        "optimizer": {
            "en": "🎯 Your Optimizer quota is full. Upgrade to Autopilot for unlimited statements!",
            "zh": "🎯 您的 Optimizer 额度已满。升级至 Autopilot 可获得无限账单！"
        },
        "autopilot": {
            "en": "⚠️ You've reached your monthly limit. Your quota resets next month.",
            "zh": "⚠️ 您已达到本月额度。额度将在下月重置。"
        }
    }
    
    @staticmethod
    def get_month_boundaries() -> tuple[datetime, datetime]:
        """Get start and end of current month"""
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate next month
        if now.month == 12:
            period_end = period_start.replace(year=now.year + 1, month=1)
        else:
            period_end = period_start.replace(month=now.month + 1)
        
        return period_start, period_end
    
    @staticmethod
    def get_or_create_quota(db: Session, user: User) -> Quota:
        """Get or create current month's quota for user"""
        period_start, period_end = QuotaService.get_month_boundaries()
        
        # Try to get existing quota (unique per user)
        quota = db.query(Quota).filter(
            Quota.user_id == user.id
        ).first()
        
        if not quota:
            # Create new quota for this month
            tier_limit = QuotaService.TIER_QUOTAS.get(user.tier, QuotaService.TIER_QUOTAS["analyst"])
            stmt_limit = QuotaService.STATEMENT_QUOTAS.get(user.tier, QuotaService.STATEMENT_QUOTAS["analyst"])
            quota = Quota(
                user_id=user.id,
                period_start=period_start,
                period_end=period_end,
                ai_calls_used=0,
                ai_calls_limit=tier_limit,
                statements_parsed=0,
                statements_limit=stmt_limit,
                files_parsed=0
            )
            db.add(quota)
            db.commit()
            db.refresh(quota)
            logger.info(f"Created new quota for user {user.id} (tier: {user.tier}, statements: {stmt_limit}, ai_calls: {tier_limit})")
        
        return quota
    
    @staticmethod
    def check_ai_quota(db: Session, user: User, locale: str = "en") -> None:
        """
        Check if user has AI quota available
        Raises QuotaExceeded if limit reached
        """
        quota = QuotaService.get_or_create_quota(db, user)
        tier_limit = QuotaService.TIER_QUOTAS.get(user.tier, QuotaService.TIER_QUOTAS["analyst"])
        
        if quota.ai_calls_used >= tier_limit:
            # Determine upgrade tier
            upgrade_tier = "optimizer" if user.tier == "analyst" else "autopilot"
            if user.tier == "autopilot":
                upgrade_tier = None  # Already at highest tier
            
            # Get localized message
            prompt = QuotaService.UPGRADE_PROMPTS[user.tier].get(locale, 
                     QuotaService.UPGRADE_PROMPTS[user.tier]["en"])
            
            logger.warning(f"User {user.id} exceeded AI quota: {quota.ai_calls_used}/{tier_limit}")
            raise QuotaExceeded(prompt, upgrade_tier)
    
    @staticmethod
    def increment_ai_calls(db: Session, user: User, count: int = 1) -> Quota:
        """Increment AI call counter for user"""
        quota = QuotaService.get_or_create_quota(db, user)
        quota.ai_calls_used += count
        db.commit()
        db.refresh(quota)
        
        tier_limit = QuotaService.TIER_QUOTAS.get(user.tier, QuotaService.TIER_QUOTAS["analyst"])
        logger.debug(f"User {user.id} AI calls: {quota.ai_calls_used}/{tier_limit}")
        
        return quota
    
    @staticmethod
    def check_statement_quota(db: Session, user: User, locale: str = "en") -> None:
        """
        Check if user can parse another statement
        Raises QuotaExceeded if limit reached
        """
        quota = QuotaService.get_or_create_quota(db, user)
        stmt_limit = QuotaService.STATEMENT_QUOTAS.get(user.tier, QuotaService.STATEMENT_QUOTAS["analyst"])
        
        if quota.statements_parsed >= stmt_limit:
            # Determine upgrade tier
            upgrade_tier = "optimizer" if user.tier == "analyst" else "autopilot"
            if user.tier == "autopilot":
                upgrade_tier = None  # Already at highest tier
            
            # Get localized message
            prompt = QuotaService.UPGRADE_PROMPTS[user.tier].get(locale, 
                     QuotaService.UPGRADE_PROMPTS[user.tier]["en"])
            
            logger.warning(f"User {user.id} exceeded statement quota: {quota.statements_parsed}/{stmt_limit}")
            raise QuotaExceeded(prompt, upgrade_tier)
    
    @staticmethod
    def increment_statements_parsed(db: Session, user: User, count: int = 1) -> Quota:
        """Increment statements parsed counter for user"""
        quota = QuotaService.get_or_create_quota(db, user)
        quota.statements_parsed += count
        db.commit()
        db.refresh(quota)
        
        stmt_limit = QuotaService.STATEMENT_QUOTAS.get(user.tier, QuotaService.STATEMENT_QUOTAS["analyst"])
        logger.debug(f"User {user.id} statements parsed: {quota.statements_parsed}/{stmt_limit}")
        
        return quota
    
    @staticmethod
    def increment_files_parsed(db: Session, user: User, count: int = 1) -> Quota:
        """Increment files parsed counter for user"""
        quota = QuotaService.get_or_create_quota(db, user)
        quota.files_parsed += count
        db.commit()
        db.refresh(quota)
        
        logger.debug(f"User {user.id} files parsed: {quota.files_parsed}")
        return quota
    
    @staticmethod
    def get_quota_status(db: Session, user: User) -> dict:
        """Get current quota status for user"""
        quota = QuotaService.get_or_create_quota(db, user)
        tier_limit = QuotaService.TIER_QUOTAS.get(user.tier, QuotaService.TIER_QUOTAS["analyst"])
        stmt_limit = QuotaService.STATEMENT_QUOTAS.get(user.tier, QuotaService.STATEMENT_QUOTAS["analyst"])
        
        return {
            "tier": user.tier,
            # Primary: Statement-based quota
            "statements_parsed": quota.statements_parsed,
            "statements_limit": stmt_limit,
            "statements_remaining": max(0, stmt_limit - quota.statements_parsed),
            # Secondary: AI call quota (for unknown merchants)
            "ai_calls_used": quota.ai_calls_used,
            "ai_calls_limit": tier_limit,
            "ai_calls_remaining": max(0, tier_limit - quota.ai_calls_used),
            # Legacy
            "files_parsed": quota.files_parsed,
            "period_start": quota.period_start.isoformat(),
            "period_end": quota.period_end.isoformat(),
            "is_exceeded": quota.statements_parsed >= stmt_limit
        }
    
    @staticmethod
    def reset_quota(db: Session, user: User) -> Quota:
        """Reset quota for user (useful for tier upgrades)"""
        period_start, period_end = QuotaService.get_month_boundaries()
        
        quota = db.query(Quota).filter(
            Quota.user_id == user.id
        ).first()
        
        if quota:
            quota.ai_calls_used = 0
            quota.statements_parsed = 0
            quota.files_parsed = 0
            db.commit()
            db.refresh(quota)
            logger.info(f"Reset quota for user {user.id}")
        else:
            quota = QuotaService.get_or_create_quota(db, user)
        
        return quota
