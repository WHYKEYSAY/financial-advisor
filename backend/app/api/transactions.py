"""
Transactions API endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger

from app.core.db import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, Transaction, Merchant, Statement
from app.schemas.transactions import (
    TransactionResponse,
    TransactionListResponse,
    CategoryBreakdownResponse
)
from app.services.categorization import categorization_service


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    institution: Optional[str] = None,
    account_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List transactions with filtering and pagination
    
    Filters:
    - category: Filter by category
    - institution: Filter by bank (CIBC, RBC, MBNA, PC Financial, etc.)
    - account_type: Filter by account type (credit_card, checking, savings)
    - start_date: Filter by start date
    - end_date: Filter by end date
    - search: Search in merchant name
    """
    # Build query
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    )
    
    # Apply filters
    if category:
        query = query.filter(Transaction.category == category)
    
    if institution:
        # Join with Statement to filter by institution
        query = query.join(Statement, Transaction.statement_id == Statement.id)
        query = query.filter(Statement.institution == institution)
    
    if account_type:
        # Join with Statement if not already joined
        if not institution:
            query = query.join(Statement, Transaction.statement_id == Statement.id)
        query = query.filter(Statement.account_type == account_type)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    if search:
        query = query.filter(
            Transaction.raw_merchant.ilike(f"%{search}%")
        )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    transactions = query.order_by(
        desc(Transaction.date)
    ).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # Enrich with merchant names
    response_transactions = []
    for txn in transactions:
        txn_dict = {
            "id": txn.id,
            "user_id": txn.user_id,
            "date": txn.date,
            "amount": txn.amount,
            "currency": txn.currency,
            "raw_merchant": txn.raw_merchant,
            "merchant_id": txn.merchant_id,
            "merchant_name": None,
            "category": txn.category,
            "subcategory": txn.subcategory,
            "tags": txn.tags or [],
            "created_at": txn.created_at
        }
        
        # Get merchant name if available
        if txn.merchant_id:
            merchant = db.query(Merchant).filter(Merchant.id == txn.merchant_id).first()
            if merchant:
                txn_dict["merchant_name"] = merchant.canonical_name
        
        response_transactions.append(TransactionResponse(**txn_dict))
    
    return TransactionListResponse(
        transactions=response_transactions,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/breakdown", response_model=List[CategoryBreakdownResponse])
def get_category_breakdown(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    institution: Optional[str] = None,
    account_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get spending breakdown by category
    
    Optional filters:
    - start_date/end_date: Date range (default: last 30 days)
    - institution: Filter by bank
    - account_type: Filter by account type
    
    Returns total spent per category with percentages
    """
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query category totals
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    )
    
    # Apply institution/account_type filters
    if institution or account_type:
        query = query.join(Statement, Transaction.statement_id == Statement.id)
        if institution:
            query = query.filter(Statement.institution == institution)
        if account_type:
            query = query.filter(Statement.account_type == account_type)
    
    results = query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.category != None
    ).group_by(
        Transaction.category
    ).all()
    
    # Calculate total for percentages (use absolute values for spending)
    grand_total = sum(abs(r.total) for r in results if r.total < 0)
    
    # Build response
    breakdown = []
    for result in results:
        if result.total < 0:  # Only negative amounts (spending)
            amount = abs(result.total)
            percentage = (amount / grand_total * 100) if grand_total > 0 else 0
            breakdown.append(CategoryBreakdownResponse(
                category=result.category,
                total=float(amount),
                percentage=round(percentage, 2),
                count=result.count
            ))
    
    # Sort by total descending
    breakdown.sort(key=lambda x: x.total, reverse=True)
    
    return breakdown


@router.get("/stats")
def get_transaction_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    institution: Optional[str] = None,
    account_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction statistics
    
    Optional filters:
    - start_date/end_date: Date range (default: last 30 days)
    - institution: Filter by bank
    - account_type: Filter by account type
    
    Returns:
    - Total transactions
    - Total spent
    - Average transaction
    - Top merchant
    - Top category
    """
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get transactions
    query = db.query(Transaction)
    
    # Apply institution/account_type filters
    if institution or account_type:
        query = query.join(Statement, Transaction.statement_id == Statement.id)
        if institution:
            query = query.filter(Statement.institution == institution)
        if account_type:
            query = query.filter(Statement.account_type == account_type)
    
    transactions = query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()
    
    if not transactions:
        return {
            "total_transactions": 0,
            "total_spent": 0,
            "average_transaction": 0,
            "top_merchant": None,
            "top_category": None
        }
    
    # Calculate stats (negative amounts are spending)
    spending_txns = [t for t in transactions if t.amount < 0]
    total_spent = sum(abs(t.amount) for t in spending_txns)
    avg_transaction = total_spent / len(spending_txns) if spending_txns else 0
    
    # Top merchant
    merchant_totals = {}
    for txn in spending_txns:
        if txn.merchant_id:
            merchant = db.query(Merchant).filter(Merchant.id == txn.merchant_id).first()
            if merchant:
                name = merchant.canonical_name
            else:
                name = txn.raw_merchant
        else:
            name = txn.raw_merchant
        
        merchant_totals[name] = merchant_totals.get(name, 0) + abs(txn.amount)
    
    top_merchant = max(merchant_totals.items(), key=lambda x: x[1])[0] if merchant_totals else None
    
    # Top category
    category_totals = {}
    for txn in spending_txns:
        if txn.category:
            category_totals[txn.category] = category_totals.get(txn.category, 0) + abs(txn.amount)
    
    top_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else None
    
    return {
        "total_transactions": len(transactions),
        "total_spent": round(total_spent, 2),
        "average_transaction": round(avg_transaction, 2),
        "top_merchant": top_merchant,
        "top_category": top_category,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }


@router.post("/{transaction_id}/categorize")
def recategorize_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger re-categorization of a transaction
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Re-categorize
    canonical_name, category = categorization_service.categorize_transaction(transaction, db)
    
    db.commit()
    db.refresh(transaction)
    
    logger.info(f"Re-categorized transaction {transaction_id}: {category}")
    
    return {
        "message": "Transaction re-categorized",
        "transaction_id": transaction_id,
        "category": category,
        "merchant": canonical_name
    }
