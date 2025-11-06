"""
Quota management API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_active_user
from app.models.models import User
from app.services.quota import QuotaService


router = APIRouter(prefix="/quota", tags=["quota"])


@router.get("/status")
def get_quota_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current quota status for authenticated user
    
    Returns:
        - tier: Current user tier
        - ai_calls_used: Number of AI calls used this month
        - ai_calls_limit: Total AI calls allowed this month
        - ai_calls_remaining: Remaining AI calls
        - files_parsed: Number of files parsed this month
        - period_start: Start of current quota period
        - period_end: End of current quota period
        - is_exceeded: Whether quota is exceeded
    """
    status = QuotaService.get_quota_status(db, current_user)
    return status


@router.post("/reset")
def reset_quota(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reset quota for current user (admin/support use)
    
    This endpoint is useful for:
    - Manual quota resets after tier upgrades
    - Support interventions
    - Testing purposes
    """
    quota = QuotaService.reset_quota(db, current_user)
    return {
        "message": "Quota reset successfully",
        "quota": QuotaService.get_quota_status(db, current_user)
    }
