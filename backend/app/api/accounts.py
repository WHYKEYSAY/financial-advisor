"""
Accounts API endpoints - for viewing account-level statistics
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger

from app.core.db import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, Transaction, Statement
from app.schemas.transactions import CategoryBreakdownResponse


router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/summary")
def get_accounts_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of all accounts grouped by type
    
    Shows separate summaries for:
    - Credit Cards (spending focus)
    - Checking/Savings (cash flow focus)
    """
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get all statements with their account types
    statements_query = db.query(
        Statement.institution,
        Statement.account_type
    ).filter(
        Statement.user_id == current_user.id,
        Statement.institution != None
    ).distinct()
    
    credit_cards = []
    checking_savings = []
    
    for stmt in statements_query.all():
        # Get transactions for this account
        txns = db.query(Transaction).join(
            Statement, Transaction.statement_id == Statement.id
        ).filter(
            Statement.user_id == current_user.id,
            Statement.institution == stmt.institution,
            Statement.account_type == stmt.account_type,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        if not txns:
            continue
        
        if stmt.account_type == "credit_card":
            spending = sum(abs(t.amount) for t in txns if t.amount < 0)
            payments = sum(t.amount for t in txns if t.amount > 0)
            credit_cards.append({
                "institution": stmt.institution,
                "total_spent": round(spending, 2),
                "total_payments": round(payments, 2),
                "net_balance": round(payments - spending, 2),
                "transaction_count": len(txns)
            })
        else:
            withdrawals = sum(abs(t.amount) for t in txns if t.amount < 0)
            deposits = sum(t.amount for t in txns if t.amount > 0)
            checking_savings.append({
                "institution": stmt.institution,
                "account_type": stmt.account_type,
                "total_withdrawals": round(withdrawals, 2),
                "total_deposits": round(deposits, 2),
                "net_flow": round(deposits - withdrawals, 2),
                "transaction_count": len(txns)
            })
    
    # Calculate totals
    total_credit_spending = sum(cc["total_spent"] for cc in credit_cards)
    total_credit_payments = sum(cc["total_payments"] for cc in credit_cards)
    total_withdrawals = sum(cs["total_withdrawals"] for cs in checking_savings)
    total_deposits = sum(cs["total_deposits"] for cs in checking_savings)
    
    return {
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "credit_cards": {
            "accounts": credit_cards,
            "total_spent": round(total_credit_spending, 2),
            "total_payments": round(total_credit_payments, 2),
            "net_balance": round(total_credit_payments - total_credit_spending, 2)
        },
        "checking_savings": {
            "accounts": checking_savings,
            "total_withdrawals": round(total_withdrawals, 2),
            "total_deposits": round(total_deposits, 2),
            "net_flow": round(total_deposits - total_withdrawals, 2)
        }
    }


@router.get("/list")
def list_accounts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all unique bank accounts from user's statements
    
    Returns list of unique combinations of institution + account_type
    """
    results = db.query(
        Statement.institution,
        Statement.account_type,
        func.count(Statement.id).label('statement_count'),
        func.min(Statement.period_start).label('first_statement'),
        func.max(Statement.period_end).label('last_statement')
    ).filter(
        Statement.user_id == current_user.id,
        Statement.institution != None
    ).group_by(
        Statement.institution,
        Statement.account_type
    ).all()
    
    accounts = []
    for result in results:
        # Count transactions for this account
        txn_count = db.query(func.count(Transaction.id)).join(
            Statement, Transaction.statement_id == Statement.id
        ).filter(
            Statement.user_id == current_user.id,
            Statement.institution == result.institution,
            Statement.account_type == result.account_type
        ).scalar()
        
        accounts.append({
            "institution": result.institution,
            "account_type": result.account_type,
            "statement_count": result.statement_count,
            "transaction_count": txn_count,
            "first_statement": result.first_statement.isoformat() if result.first_statement else None,
            "last_statement": result.last_statement.isoformat() if result.last_statement else None
        })
    
    return {
        "accounts": accounts,
        "total": len(accounts)
    }


@router.get("/breakdown")
def get_account_breakdown(
    institution: str = Query(..., description="Bank institution (CIBC, RBC, MBNA, etc.)"),
    account_type: Optional[str] = Query(None, description="Account type (credit_card, checking, savings)"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get spending breakdown by category for a specific account
    
    Required:
    - institution: Bank name
    
    Optional:
    - account_type: Filter by account type
    - start_date/end_date: Date range (default: last 30 days)
    """
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Query category totals for this account
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).join(
        Statement, Transaction.statement_id == Statement.id
    ).filter(
        Statement.user_id == current_user.id,
        Statement.institution == institution,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.category != None
    )
    
    if account_type:
        query = query.filter(Statement.account_type == account_type)
    
    results = query.group_by(Transaction.category).all()
    
    # Calculate total for percentages (use absolute values for spending)
    grand_total = sum(abs(r.total) for r in results if r.total < 0)
    
    # Build response
    breakdown = []
    for result in results:
        if result.total < 0:  # Only negative amounts (spending)
            amount = abs(result.total)
            percentage = (amount / grand_total * 100) if grand_total > 0 else 0
            breakdown.append({
                "category": result.category,
                "total": float(amount),
                "percentage": round(percentage, 2),
                "count": result.count
            })
    
    # Sort by total descending
    breakdown.sort(key=lambda x: x['total'], reverse=True)
    
    return {
        "institution": institution,
        "account_type": account_type,
        "breakdown": breakdown,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }


@router.get("/stats")
def get_account_stats(
    institution: str = Query(..., description="Bank institution"),
    account_type: Optional[str] = Query(None, description="Account type"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction statistics for a specific account
    
    Returns different stats based on account type:
    
    Credit Cards:
    - total_spent: Total charges
    - total_payments: Total payments made
    - net_balance: Payments - Charges (negative = owed)
    - average_charge: Average spending per transaction
    - charge_count / payment_count
    
    Checking/Savings:
    - total_withdrawals: Total outflows
    - total_deposits: Total inflows
    - net_flow: Deposits - Withdrawals (negative = net outflow)
    - average_withdrawal: Average per withdrawal
    - withdrawal_count / deposit_count
    
    Both:
    - top_merchant, top_category (based on outflows)
    """
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get transactions for this account
    query = db.query(Transaction).join(
        Statement, Transaction.statement_id == Statement.id
    ).filter(
        Statement.user_id == current_user.id,
        Statement.institution == institution,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    )
    
    if account_type:
        query = query.filter(Statement.account_type == account_type)
    
    transactions = query.all()
    
    if not transactions:
        return {
            "institution": institution,
            "account_type": account_type,
            "total_transactions": 0,
            "total_spent": 0,
            "average_transaction": 0,
            "top_merchant": None,
            "top_category": None
        }
    
    # Different logic for credit cards vs debit/checking accounts
    is_credit_card = account_type == "credit_card"
    
    if is_credit_card:
        # Credit card: negative = spending (charges)
        spending_txns = [t for t in transactions if t.amount < 0]
        payment_txns = [t for t in transactions if t.amount > 0]
        total_spent = sum(abs(t.amount) for t in spending_txns)
        total_payments = sum(t.amount for t in payment_txns)
        avg_transaction = total_spent / len(spending_txns) if spending_txns else 0
    else:
        # Checking/Savings: negative = withdrawal/transfer (outflow)
        withdrawal_txns = [t for t in transactions if t.amount < 0]
        deposit_txns = [t for t in transactions if t.amount > 0]
        total_spent = sum(abs(t.amount) for t in withdrawal_txns)
        total_deposits = sum(t.amount for t in deposit_txns)
        avg_transaction = total_spent / len(withdrawal_txns) if withdrawal_txns else 0
    
    # Use appropriate transactions list for merchant/category analysis
    analysis_txns = spending_txns if is_credit_card else withdrawal_txns
    
    # Top merchant
    merchant_totals = {}
    for txn in analysis_txns:
        name = txn.raw_merchant or "Unknown"
        merchant_totals[name] = merchant_totals.get(name, 0) + abs(txn.amount)
    
    top_merchant = max(merchant_totals.items(), key=lambda x: x[1])[0] if merchant_totals else None
    
    # Top category
    category_totals = {}
    for txn in analysis_txns:
        if txn.category:
            category_totals[txn.category] = category_totals.get(txn.category, 0) + abs(txn.amount)
    
    top_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else None
    
    # Build response with different fields for credit card vs debit
    response = {
        "institution": institution,
        "account_type": account_type,
        "total_transactions": len(transactions),
        "top_merchant": top_merchant,
        "top_category": top_category,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }
    
    if is_credit_card:
        # Credit card specific stats
        response.update({
            "total_spent": round(total_spent, 2),
            "total_payments": round(total_payments, 2),
            "net_balance": round(total_payments - total_spent, 2),  # positive = overpaid, negative = owed
            "average_charge": round(avg_transaction, 2),
            "charge_count": len(spending_txns),
            "payment_count": len(payment_txns)
        })
    else:
        # Checking/Savings specific stats
        response.update({
            "total_withdrawals": round(total_spent, 2),
            "total_deposits": round(total_deposits, 2),
            "net_flow": round(total_deposits - total_spent, 2),  # positive = net deposit, negative = net withdrawal
            "average_withdrawal": round(avg_transaction, 2),
            "withdrawal_count": len(withdrawal_txns),
            "deposit_count": len(deposit_txns)
        })
    
    return response
