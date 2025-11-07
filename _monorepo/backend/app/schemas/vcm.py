"""
Pydantic schemas for Virtual Credit Manager (VCM)
"""
from typing import List, Optional
from decimal import Decimal
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class HealthStatus(str, Enum):
    """Credit utilization health status"""
    OPTIMAL = "optimal"  # 10-30%
    UNDERUTILIZED = "underutilized"  # <10%
    ELEVATED = "elevated"  # 30-50%
    HIGH = "high"  # >50%
    N_A = "n_a"  # Unable to calculate


class CardSummary(BaseModel):
    """Summary of a single credit card's status"""
    card_id: int = Field(..., description="Card ID")
    issuer: str = Field(..., description="Card issuer (e.g., RBC, MBNA)")
    product: str = Field(..., description="Card product name")
    credit_limit: Decimal = Field(..., description="Credit limit (CAD)")
    current_balance: Decimal = Field(..., description="Current outstanding balance (CAD)")
    utilization_rate: Decimal = Field(..., description="Credit utilization rate (%)")
    health_status: HealthStatus = Field(..., description="Health status based on utilization")
    last4: Optional[str] = Field(None, description="Last 4 digits of card number")

    @field_validator('credit_limit', 'current_balance', 'utilization_rate', mode='before')
    @classmethod
    def round_decimals(cls, v):
        """Round all decimal fields to 2 decimal places"""
        if v is None:
            return Decimal('0.00')
        return Decimal(str(v)).quantize(Decimal('0.01'))

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": 1,
                "issuer": "RBC",
                "product": "Avion Visa Infinite",
                "credit_limit": 10000.00,
                "current_balance": 2500.00,
                "utilization_rate": 25.00,
                "health_status": "optimal",
                "last4": "1234"
            }
        }


class CreditOverviewResponse(BaseModel):
    """Complete credit overview across all cards"""
    total_credit_limit: Decimal = Field(..., description="Total credit limit across all cards (CAD)")
    total_used: Decimal = Field(..., description="Total used credit across all cards (CAD)")
    overall_utilization: Decimal = Field(..., description="Overall credit utilization rate (%)")
    health_status: HealthStatus = Field(..., description="Overall health status")
    cards_summary: List[CardSummary] = Field(..., description="Summary of each card")

    @field_validator('total_credit_limit', 'total_used', 'overall_utilization', mode='before')
    @classmethod
    def round_decimals(cls, v):
        """Round all decimal fields to 2 decimal places"""
        if v is None:
            return Decimal('0.00')
        return Decimal(str(v)).quantize(Decimal('0.01'))

    class Config:
        json_schema_extra = {
            "example": {
                "total_credit_limit": 25000.00,
                "total_used": 5000.00,
                "overall_utilization": 20.00,
                "health_status": "optimal",
                "cards_summary": []
            }
        }


class UtilizationResponse(BaseModel):
    """Credit utilization analysis"""
    overall_utilization: Decimal = Field(..., description="Overall credit utilization rate (%)")
    health_status: HealthStatus = Field(..., description="Overall health status")
    per_card: List[CardSummary] = Field(..., description="Utilization breakdown per card")

    @field_validator('overall_utilization', mode='before')
    @classmethod
    def round_decimals(cls, v):
        """Round all decimal fields to 2 decimal places"""
        if v is None:
            return Decimal('0.00')
        return Decimal(str(v)).quantize(Decimal('0.01'))

    class Config:
        json_schema_extra = {
            "example": {
                "overall_utilization": 20.00,
                "health_status": "optimal",
                "per_card": []
            }
        }


class AddCardRequest(BaseModel):
    """Request to add a new credit card"""
    issuer: str = Field(..., description="Card issuer", min_length=1, max_length=100)
    product: str = Field(..., description="Card product name", min_length=1, max_length=100)
    credit_limit: Decimal = Field(..., description="Credit limit (CAD)", gt=0)
    last4: Optional[str] = Field(None, description="Last 4 digits", min_length=4, max_length=4)
    statement_day: Optional[int] = Field(None, description="Statement day of month (1-31)", ge=1, le=31)
    due_day: Optional[int] = Field(None, description="Payment due day of month (1-31)", ge=1, le=31)

    @field_validator('credit_limit', mode='before')
    @classmethod
    def round_limit(cls, v):
        """Round credit limit to 2 decimal places"""
        return Decimal(str(v)).quantize(Decimal('0.01'))

    class Config:
        json_schema_extra = {
            "example": {
                "issuer": "RBC",
                "product": "Avion Visa Infinite",
                "credit_limit": 10000.00,
                "last4": "1234",
                "statement_day": 15,
                "due_day": 5
            }
        }


class AddCardResponse(BaseModel):
    """Response after adding a credit card"""
    card_id: int = Field(..., description="Created card ID")
    issuer: str
    product: str
    credit_limit: Decimal
    last4: Optional[str] = None
    message: str = Field(default="Card added successfully")

    @field_validator('credit_limit', mode='before')
    @classmethod
    def round_limit(cls, v):
        """Round credit limit to 2 decimal places"""
        if v is None:
            return Decimal('0.00')
        return Decimal(str(v)).quantize(Decimal('0.01'))


class PaymentReminderResponse(BaseModel):
    """Payment reminder for a credit card"""
    card_id: int = Field(..., description="Card ID")
    issuer: str = Field(..., description="Card issuer")
    product: str = Field(..., description="Card product name")
    due_date: date = Field(..., description="Payment due date")
    days_until_due: int = Field(..., description="Days until payment is due")
    current_balance: Optional[Decimal] = Field(None, description="Current outstanding balance (CAD)")
    minimum_payment: Optional[Decimal] = Field(None, description="Minimum payment amount (CAD)")
    statement_balance: Optional[Decimal] = Field(None, description="Statement balance (CAD)")

    @field_validator('current_balance', 'minimum_payment', 'statement_balance', mode='before')
    @classmethod
    def round_decimals(cls, v):
        """Round all decimal fields to 2 decimal places"""
        if v is None:
            return None
        return Decimal(str(v)).quantize(Decimal('0.01'))

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": 1,
                "issuer": "RBC",
                "product": "Avion Visa Infinite",
                "due_date": "2025-11-15",
                "days_until_due": 9,
                "current_balance": 2500.00,
                "minimum_payment": 50.00,
                "statement_balance": 2500.00
            }
        }


class SpendingAllocationRequest(BaseModel):
    """Request to optimize spending allocation across cards"""
    amount: Decimal = Field(..., description="Amount to spend (CAD)", gt=0)
    
    @field_validator('amount', mode='before')
    @classmethod
    def round_amount(cls, v):
        """Round amount to 2 decimal places"""
        return Decimal(str(v)).quantize(Decimal('0.01'))
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 1500.00
            }
        }


class CardPaymentStep(BaseModel):
    """A step in the payment allocation plan"""
    card_id: int = Field(..., description="Card ID")
    issuer: str = Field(..., description="Card issuer")
    product: str = Field(..., description="Card product name")
    last4: Optional[str] = Field(None, description="Last 4 digits")
    amount_to_charge: Decimal = Field(..., description="Amount to charge on this card (CAD)")
    current_utilization: Decimal = Field(..., description="Current utilization rate (%)")
    new_utilization: Decimal = Field(..., description="Utilization after this charge (%)")
    available_credit: Decimal = Field(..., description="Available credit before charge (CAD)")
    reason: str = Field(..., description="Why this allocation was chosen")
    
    @field_validator('amount_to_charge', 'available_credit', mode='before')
    @classmethod
    def round_money(cls, v):
        """Round monetary amounts to 2 decimal places"""
        if v is None:
            return Decimal('0.00')
        return Decimal(str(v)).quantize(Decimal('0.01'))
    
    @field_validator('current_utilization', 'new_utilization', mode='before')
    @classmethod
    def round_utilization(cls, v):
        """Round utilization to 2 decimal places"""
        if v is None:
            return Decimal('0.00')
        return Decimal(str(v)).quantize(Decimal('0.01'))
    
    class Config:
        json_schema_extra = {
            "example": {
                "card_id": 1,
                "issuer": "RBC",
                "product": "Avion Visa Infinite",
                "last4": "1234",
                "amount_to_charge": 800.00,
                "current_utilization": 15.00,
                "new_utilization": 23.00,
                "available_credit": 8500.00,
                "reason": "Lowest utilization, stays within optimal range (10-30%)"
            }
        }


class SpendingAllocationResponse(BaseModel):
    """Optimized spending allocation plan across multiple cards"""
    total_amount: Decimal = Field(..., description="Total amount to spend (CAD)")
    allocation_feasible: bool = Field(..., description="Whether the allocation is possible")
    allocation_steps: List[CardPaymentStep] = Field(..., description="Step-by-step payment instructions")
    optimization_summary: str = Field(..., description="Summary of optimization strategy")
    total_available_credit: Decimal = Field(..., description="Total available credit (CAD)")
    warnings: List[str] = Field(default_factory=list, description="Warnings or concerns")
    
    @field_validator('total_amount', 'total_available_credit', mode='before')
    @classmethod
    def round_money(cls, v):
        """Round monetary amounts to 2 decimal places"""
        if v is None:
            return Decimal('0.00')
        return Decimal(str(v)).quantize(Decimal('0.01'))
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_amount": 1500.00,
                "allocation_feasible": True,
                "allocation_steps": [],
                "optimization_summary": "Allocated across 2 cards to maintain optimal utilization (10-30%)",
                "total_available_credit": 15000.00,
                "warnings": []
            }
        }
