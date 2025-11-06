"""
File upload and statement schemas
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class StatementResponse(BaseModel):
    """Statement response model"""
    id: int
    user_id: int
    source_type: Literal["pdf", "csv", "image"]
    file_path: str
    parsed: bool
    
    # Bank/account identification
    institution: Optional[str] = None
    account_type: Optional[str] = None
    account_number: Optional[str] = None
    
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StatementListResponse(BaseModel):
    """List of statements response"""
    statements: list[StatementResponse]
    total: int
    page: int
    page_size: int


class StatementStatusResponse(BaseModel):
    """Statement parsing status response"""
    id: int
    parsed: bool
    transaction_count: int
    error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class UploadResponse(BaseModel):
    """File upload response"""
    statement_id: int
    filename: str
    size_bytes: int
    source_type: str
    message: str
