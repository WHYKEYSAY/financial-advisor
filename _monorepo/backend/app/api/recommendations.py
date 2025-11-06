"""
Credit Card Recommendations API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.models import User
from app.services.rewards_calculator import RewardsCalculator
from app.schemas.recommendations import CardRecommendationResponse


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/cards", response_model=list[CardRecommendationResponse])
def get_card_recommendations(
    months: int = Query(default=12, ge=1, le=36, description="Months of transaction history to analyze"),
    welcome_bonus_years: Optional[int] = Query(default=None, ge=1, le=10, description="Years to amortize welcome bonus"),
    min_income: Optional[int] = Query(default=None, ge=0, description="Minimum income requirement filter"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of cards to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized credit card recommendations based on user's spending patterns.
    
    Returns cards sorted by Net Annual Value (NAV):
    - NAV = Annual Rewards + Amortized Welcome Bonus - Annual Fee
    
    **Parameters:**
    - `months`: Number of months of transaction history to analyze (default: 12)
    - `welcome_bonus_years`: Years to amortize welcome bonus over (default: 3)
    - `min_income`: Filter cards by minimum income requirement
    - `limit`: Maximum number of recommendations to return (default: 10)
    
    **Returns:**
    List of credit card recommendations with NAV breakdown, sorted by NAV (highest first).
    """
    calculator = RewardsCalculator(db)
    
    recommendations = calculator.recommend_cards(
        user_id=current_user.id,
        months=months,
        welcome_bonus_years=welcome_bonus_years,
        min_income=min_income,
        limit=limit
    )
    
    return recommendations
