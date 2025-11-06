"""
Transaction schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TransactionResponse(BaseModel):
    """Transaction response model"""
    id: int
    user_id: int
    date: datetime
    amount: float
    currency: str
    raw_merchant: str
    merchant_id: Optional[int] = None
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """List of transactions response"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int


class CategoryBreakdownResponse(BaseModel):
    """Category spending breakdown"""
    category: str
    total: float
    percentage: float
    count: int
