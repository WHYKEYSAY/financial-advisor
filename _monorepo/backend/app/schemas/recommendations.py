"""
Pydantic schemas for credit card recommendations
"""
from typing import Optional
from pydantic import BaseModel, Field


class CardRecommendationResponse(BaseModel):
    """Credit card recommendation with NAV breakdown"""
    
    nav: float = Field(..., description="Net Annual Value (CAD)")
    annual_rewards: float = Field(..., description="Expected annual rewards (CAD)")
    welcome_bonus_amortized: float = Field(..., description="Amortized welcome bonus (CAD/year)")
    annual_fee: float = Field(..., description="Annual fee (CAD)")
    
    card_id: int = Field(..., description="Credit card database ID")
    issuer: str = Field(..., description="Card issuer (e.g., MBNA, RBC)")
    product_name: str = Field(..., description="Card product name")
    card_network: Optional[str] = Field(None, description="Card network (Visa, Mastercard, Amex)")
    
    min_income: Optional[int] = Field(None, description="Minimum personal income requirement")
    min_household_income: Optional[int] = Field(None, description="Minimum household income requirement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nav": 450.0,
                "annual_rewards": 400.0,
                "welcome_bonus_amortized": 100.0,
                "annual_fee": 50.0,
                "card_id": 1,
                "issuer": "MBNA",
                "product_name": "Rewards World Elite Mastercard",
                "card_network": "Mastercard",
                "min_income": 80000,
                "min_household_income": 150000
            }
        }
