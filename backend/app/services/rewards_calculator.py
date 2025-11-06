"""
Rewards Calculator Service - NAV (Net Annual Value) calculation engine

Calculates the expected annual rewards for each credit card based on:
1. User's historical spending patterns by category
2. Card's rewards structure (cashback, points, etc.)
3. Welcome bonus amortized over expected holding period
4. Annual fees and costs

NAV = Annual Rewards + Amortized Welcome Bonus - Annual Fee
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.models import Transaction, CreditCard


class RewardsCalculator:
    """Calculate Net Annual Value (NAV) for credit cards"""
    
    DEFAULT_WELCOME_BONUS_YEARS = 3  # Amortize welcome bonus over 3 years
    POINTS_TO_CAD_RATIO = 0.01  # Default: 100 points = $1 CAD
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_spending_profile(
        self, 
        user_id: int, 
        months: int = 12
    ) -> Dict[str, float]:
        """
        Analyze user's spending patterns by category over the last N months.
        
        Args:
            user_id: User ID
            months: Number of months to analyze (default 12)
            
        Returns:
            Dict mapping category name to annual spending amount
            Example: {"groceries": 6000.0, "gas": 2400.0, "dining": 3600.0, "default": 12000.0}
        """
        cutoff_date = datetime.now().date() - timedelta(days=months * 30)
        
        # Query transactions grouped by category
        result = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total")
        ).filter(
            Transaction.user_id == user_id,
            Transaction.date >= cutoff_date,
            Transaction.amount > 0  # Only count spending (positive amounts)
        ).group_by(Transaction.category).all()
        
        # Convert to dict and annualize
        spending_profile = {}
        for category, total in result:
            category_key = category.lower() if category else "default"
            annualized_amount = float(total) * (12 / months)
            spending_profile[category_key] = annualized_amount
        
        # Add "default" category for uncategorized spending
        if "default" not in spending_profile:
            spending_profile["default"] = 0.0
        
        return spending_profile
    
    def calculate_card_rewards(
        self, 
        credit_card: CreditCard, 
        spending_profile: Dict[str, float]
    ) -> float:
        """
        Calculate annual rewards for a specific credit card based on spending profile.
        
        Args:
            credit_card: CreditCard model instance
            spending_profile: Dict of category -> annual spending
            
        Returns:
            Annual rewards value in CAD
        """
        rewards_structure = credit_card.rewards or {}
        total_rewards = 0.0
        
        for category, annual_spending in spending_profile.items():
            # Find matching rewards category (handle variations like "grocery" vs "groceries")
            reward_info = self._match_rewards_category(rewards_structure, category)
            
            if reward_info:
                rate = reward_info.get("rate", 0.0)
                reward_type = reward_info.get("type", "cashback")
                
                if reward_type == "cashback":
                    # Cashback: rate is percentage (e.g., 3.0 = 3%)
                    rewards_value = annual_spending * (rate / 100)
                elif reward_type == "points":
                    # Points: rate is points per dollar (e.g., 3.0 = 3 points per $1)
                    points_earned = annual_spending * rate
                    rewards_value = points_earned * self.POINTS_TO_CAD_RATIO
                else:
                    rewards_value = 0.0
                
                total_rewards += rewards_value
        
        return total_rewards
    
    def calculate_welcome_bonus_value(
        self, 
        credit_card: CreditCard, 
        years: Optional[int] = None
    ) -> float:
        """
        Calculate the amortized annual value of the welcome bonus.
        
        Args:
            credit_card: CreditCard model instance
            years: Number of years to amortize over (default: 3)
            
        Returns:
            Annual amortized value in CAD
        """
        if not credit_card.welcome_bonus:
            return 0.0
        
        years = years or self.DEFAULT_WELCOME_BONUS_YEARS
        welcome_bonus = credit_card.welcome_bonus
        
        value = welcome_bonus.get("value", 0)
        bonus_type = welcome_bonus.get("type", "cashback")
        
        if bonus_type == "cashback":
            bonus_cad = float(value)
        elif bonus_type == "points":
            bonus_cad = float(value) * self.POINTS_TO_CAD_RATIO
        else:
            bonus_cad = 0.0
        
        return bonus_cad / years
    
    def calculate_nav(
        self, 
        credit_card: CreditCard, 
        spending_profile: Dict[str, float],
        welcome_bonus_years: Optional[int] = None
    ) -> Dict:
        """
        Calculate Net Annual Value (NAV) for a credit card.
        
        NAV = Annual Rewards + Amortized Welcome Bonus - Annual Fee
        
        Args:
            credit_card: CreditCard model instance
            spending_profile: User's spending profile by category
            welcome_bonus_years: Years to amortize welcome bonus over
            
        Returns:
            Dict with NAV breakdown:
            {
                "nav": 450.0,
                "annual_rewards": 400.0,
                "welcome_bonus_amortized": 100.0,
                "annual_fee": 50.0,
                "card_id": 1,
                "issuer": "MBNA",
                "product_name": "Rewards World Elite Mastercard"
            }
        """
        annual_rewards = self.calculate_card_rewards(credit_card, spending_profile)
        welcome_bonus = self.calculate_welcome_bonus_value(
            credit_card, 
            years=welcome_bonus_years
        )
        annual_fee = float(credit_card.annual_fee or 0)
        
        nav = annual_rewards + welcome_bonus - annual_fee
        
        return {
            "nav": round(nav, 2),
            "annual_rewards": round(annual_rewards, 2),
            "welcome_bonus_amortized": round(welcome_bonus, 2),
            "annual_fee": round(annual_fee, 2),
            "card_id": credit_card.id,
            "issuer": credit_card.issuer,
            "product_name": credit_card.product_name,
            "card_network": credit_card.card_network,
            "min_income": credit_card.min_income,
            "min_household_income": credit_card.min_household_income,
        }
    
    def recommend_cards(
        self, 
        user_id: int, 
        months: int = 12,
        welcome_bonus_years: Optional[int] = None,
        min_income: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Recommend credit cards sorted by NAV based on user's spending profile.
        
        Args:
            user_id: User ID
            months: Months of transaction history to analyze
            welcome_bonus_years: Years to amortize welcome bonus
            min_income: Filter cards by minimum income requirement
            limit: Maximum number of cards to return
            
        Returns:
            List of card recommendations sorted by NAV (highest first)
        """
        # Get user's spending profile
        spending_profile = self.get_user_spending_profile(user_id, months)
        
        # Get all active credit cards
        query = self.db.query(CreditCard).filter(CreditCard.is_active == True)
        
        # Filter by income requirement if provided
        if min_income is not None:
            query = query.filter(
                (CreditCard.min_income == None) | 
                (CreditCard.min_income <= min_income)
            )
        
        credit_cards = query.all()
        
        # Calculate NAV for each card
        recommendations = []
        for card in credit_cards:
            nav_data = self.calculate_nav(card, spending_profile, welcome_bonus_years)
            recommendations.append(nav_data)
        
        # Sort by NAV (highest first) and limit results
        recommendations.sort(key=lambda x: x["nav"], reverse=True)
        return recommendations[:limit]
    
    def _match_rewards_category(
        self, 
        rewards_structure: Dict, 
        category: str
    ) -> Optional[Dict]:
        """
        Match a spending category to a rewards category.
        Handles variations like "grocery" vs "groceries".
        
        Args:
            rewards_structure: Card's rewards structure
            category: Spending category to match
            
        Returns:
            Rewards info dict or None if no match
        """
        # Direct match
        if category in rewards_structure:
            return rewards_structure[category]
        
        # Try variations
        variations = [
            category.rstrip("s"),  # "groceries" -> "grocery"
            category + "s",         # "grocery" -> "groceries"
            category.replace("_", " "),
            category.replace(" ", "_"),
        ]
        
        for variant in variations:
            if variant in rewards_structure:
                return rewards_structure[variant]
        
        # Fallback to "default" category
        return rewards_structure.get("default")
