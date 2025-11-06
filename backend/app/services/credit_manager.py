"""
Credit Manager Service - VCM (Virtual Credit Manager) business logic

Provides functionality for:
- Credit utilization tracking across all cards
- Balance calculations
- Health status monitoring
- Payment reminders
"""
from typing import List, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, date
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Card, Transaction
from app.schemas.vcm import HealthStatus, CardSummary, CreditOverviewResponse, PaymentReminderResponse


def round_money(amount: Decimal) -> Decimal:
    """
    Round monetary amount to 2 decimal places using HALF_UP rounding.
    
    Args:
        amount: Decimal amount to round
        
    Returns:
        Rounded Decimal with 2 decimal places
    """
    if amount is None:
        return Decimal('0.00')
    return Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def round_rate(rate: Decimal) -> Decimal:
    """
    Round percentage rate to 2 decimal places using HALF_UP rounding.
    
    Args:
        rate: Decimal percentage to round
        
    Returns:
        Rounded Decimal with 2 decimal places
    """
    if rate is None:
        return Decimal('0.00')
    return Decimal(str(rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def utilization_health(utilization_rate: Decimal) -> HealthStatus:
    """
    Determine health status based on credit utilization rate.
    
    Health zones:
    - < 10%: underutilized
    - 10-30%: optimal
    - 30-50%: elevated
    - > 50%: high
    - Unable to calculate: n_a
    
    Args:
        utilization_rate: Credit utilization rate as percentage (0-100)
        
    Returns:
        HealthStatus enum value
    """
    if utilization_rate is None:
        return HealthStatus.N_A
    
    rate = float(utilization_rate)
    
    if rate < 10:
        return HealthStatus.UNDERUTILIZED
    elif rate <= 30:
        return HealthStatus.OPTIMAL
    elif rate <= 50:
        return HealthStatus.ELEVATED
    else:
        return HealthStatus.HIGH


def get_cards_for_user(db: Session, user_id: int) -> List[Card]:
    """
    Get all active credit cards for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of Card objects
    """
    return db.query(Card).filter(
        Card.user_id == user_id,
        Card.is_active == True
    ).all()


def get_current_balance(db: Session, card_id: int) -> Decimal:
    """
    Calculate current outstanding balance for a credit card.
    
    Logic:
    - Charges (negative amounts): Sum of all negative transaction amounts
    - Payments (positive amounts): Sum of all positive transaction amounts
    - Balance = max(0, charges - payments)
    
    Args:
        db: Database session
        card_id: Card ID
        
    Returns:
        Current balance as Decimal (always >= 0)
    """
    # Query all transactions for this card
    result = db.query(
        func.sum(
            func.case(
                (Transaction.amount < 0, func.abs(Transaction.amount)),
                else_=0
            )
        ).label('total_charges'),
        func.sum(
            func.case(
                (Transaction.amount > 0, Transaction.amount),
                else_=0
            )
        ).label('total_payments')
    ).filter(
        Transaction.card_id == card_id
    ).first()
    
    if not result or result.total_charges is None:
        return Decimal('0.00')
    
    charges = Decimal(str(result.total_charges or 0))
    payments = Decimal(str(result.total_payments or 0))
    
    # Balance is charges minus payments, but never negative (overpayment = 0 balance)
    balance = max(Decimal('0.00'), charges - payments)
    
    return round_money(balance)


def get_all_balances(db: Session, user_id: int) -> Dict[int, Decimal]:
    """
    Get balances for all cards of a user in a single optimized query.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dict mapping card_id to current balance
    """
    # Join cards with transactions and aggregate
    result = db.query(
        Card.id.label('card_id'),
        func.sum(
            func.case(
                (Transaction.amount < 0, func.abs(Transaction.amount)),
                else_=0
            )
        ).label('total_charges'),
        func.sum(
            func.case(
                (Transaction.amount > 0, Transaction.amount),
                else_=0
            )
        ).label('total_payments')
    ).outerjoin(
        Transaction, Card.id == Transaction.card_id
    ).filter(
        Card.user_id == user_id,
        Card.is_active == True
    ).group_by(Card.id).all()
    
    balances = {}
    for row in result:
        charges = Decimal(str(row.total_charges or 0))
        payments = Decimal(str(row.total_payments or 0))
        balance = max(Decimal('0.00'), charges - payments)
        balances[row.card_id] = round_money(balance)
    
    return balances


def calculate_card_utilization(credit_limit: Decimal, current_balance: Decimal) -> tuple[Decimal, HealthStatus]:
    """
    Calculate utilization rate and health status for a single card.
    
    Args:
        credit_limit: Card's credit limit
        current_balance: Card's current balance
        
    Returns:
        Tuple of (utilization_rate, health_status)
    """
    if credit_limit is None or credit_limit <= 0:
        return Decimal('0.00'), HealthStatus.N_A
    
    if current_balance is None or current_balance <= 0:
        return Decimal('0.00'), HealthStatus.UNDERUTILIZED
    
    utilization = (current_balance / credit_limit) * 100
    utilization = round_rate(utilization)
    health = utilization_health(utilization)
    
    return utilization, health


def get_credit_overview(db: Session, user_id: int) -> CreditOverviewResponse:
    """
    Get complete credit overview for a user.
    
    Returns:
        - Total credit limit across all cards
        - Total used credit
        - Overall utilization rate
        - Overall health status
        - Per-card summaries
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        CreditOverviewResponse object
    """
    # Get all cards for user
    cards = get_cards_for_user(db, user_id)
    
    if not cards:
        return CreditOverviewResponse(
            total_credit_limit=Decimal('0.00'),
            total_used=Decimal('0.00'),
            overall_utilization=Decimal('0.00'),
            health_status=HealthStatus.N_A,
            cards_summary=[]
        )
    
    # Get all balances in one query
    balances = get_all_balances(db, user_id)
    
    # Build card summaries
    cards_summary = []
    total_credit_limit = Decimal('0.00')
    total_used = Decimal('0.00')
    
    for card in cards:
        credit_limit = round_money(Decimal(str(card.credit_limit or 0)))
        current_balance = balances.get(card.id, Decimal('0.00'))
        utilization_rate, health_status = calculate_card_utilization(credit_limit, current_balance)
        
        cards_summary.append(CardSummary(
            card_id=card.id,
            issuer=card.issuer,
            product=card.product,
            credit_limit=credit_limit,
            current_balance=current_balance,
            utilization_rate=utilization_rate,
            health_status=health_status,
            last4=card.last4
        ))
        
        total_credit_limit += credit_limit
        total_used += current_balance
    
    # Calculate overall utilization
    if total_credit_limit > 0:
        overall_utilization = (total_used / total_credit_limit) * 100
        overall_utilization = round_rate(overall_utilization)
        overall_health = utilization_health(overall_utilization)
    else:
        overall_utilization = Decimal('0.00')
        overall_health = HealthStatus.N_A
    
    return CreditOverviewResponse(
        total_credit_limit=total_credit_limit,
        total_used=total_used,
        overall_utilization=overall_utilization,
        health_status=overall_health,
        cards_summary=cards_summary
    )


def get_card_summary(db: Session, card_id: int, user_id: int) -> Optional[CardSummary]:
    """
    Get summary for a specific card.
    
    Args:
        db: Database session
        card_id: Card ID
        user_id: User ID (for authorization check)
        
    Returns:
        CardSummary object or None if card not found/not owned by user
    """
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.user_id == user_id,
        Card.is_active == True
    ).first()
    
    if not card:
        return None
    
    credit_limit = round_money(Decimal(str(card.credit_limit or 0)))
    current_balance = get_current_balance(db, card_id)
    utilization_rate, health_status = calculate_card_utilization(credit_limit, current_balance)
    
    return CardSummary(
        card_id=card.id,
        issuer=card.issuer,
        product=card.product,
        credit_limit=credit_limit,
        current_balance=current_balance,
        utilization_rate=utilization_rate,
        health_status=health_status,
        last4=card.last4
    )


def get_payment_reminders(db: Session, user_id: int, days_ahead: int = 7) -> List[PaymentReminderResponse]:
    """
    Get payment reminders for cards with upcoming due dates.
    
    Returns cards that have a payment due within the next N days.
    
    Args:
        db: Database session
        user_id: User ID
        days_ahead: Number of days to look ahead (default: 7)
        
    Returns:
        List of PaymentReminderResponse objects
    """
    cards = get_cards_for_user(db, user_id)
    reminders = []
    today = date.today()
    
    for card in cards:
        if card.due_day is None:
            continue
        
        # Calculate next due date
        current_month_due = date(today.year, today.month, min(card.due_day, 28))
        
        # If due date already passed this month, use next month
        if current_month_due < today:
            if today.month == 12:
                next_due = date(today.year + 1, 1, min(card.due_day, 28))
            else:
                next_due = date(today.year, today.month + 1, min(card.due_day, 28))
        else:
            next_due = current_month_due
        
        # Check if within reminder window
        days_until = (next_due - today).days
        if 0 <= days_until <= days_ahead:
            current_balance = get_current_balance(db, card.id)
            
            # Estimate minimum payment (typically 2-3% of balance or $10, whichever is greater)
            minimum_payment = max(current_balance * Decimal('0.03'), Decimal('10.00'))
            if current_balance == 0:
                minimum_payment = Decimal('0.00')
            
            reminders.append(PaymentReminderResponse(
                card_id=card.id,
                issuer=card.issuer,
                product=card.product,
                due_date=next_due,
                days_until_due=days_until,
                current_balance=current_balance,
                minimum_payment=round_money(minimum_payment),
                statement_balance=current_balance  # Simplified: using current balance
            ))
    
    # Sort by days until due
    reminders.sort(key=lambda x: x.days_until_due)
    
    return reminders


def optimize_spending_allocation(
    db: Session, 
    user_id: int, 
    amount: Decimal
) -> dict:
    """
    Optimize spending allocation across multiple cards.
    
    Strategy:
    1. Prioritize cards with lowest utilization
    2. Keep all cards within optimal range (10-30%) when possible
    3. Avoid pushing any card above 30% utilization
    4. If unavoidable, minimize the number of cards above 30%
    
    Args:
        db: Database session
        user_id: User ID
        amount: Amount to spend
        
    Returns:
        Dict with allocation plan and metadata
    """
    from app.schemas.vcm import CardPaymentStep
    
    # Get all cards with their current status
    cards = get_cards_for_user(db, user_id)
    if not cards:
        return {
            "allocation_feasible": False,
            "allocation_steps": [],
            "optimization_summary": "No active credit cards found",
            "total_available_credit": Decimal('0.00'),
            "warnings": ["You need to add at least one credit card first"]
        }
    
    # Get current balances
    balances = get_all_balances(db, user_id)
    
    # Build card info list
    card_info = []
    total_available_credit = Decimal('0.00')
    
    for card in cards:
        credit_limit = round_money(Decimal(str(card.credit_limit or 0)))
        current_balance = balances.get(card.id, Decimal('0.00'))
        available_credit = max(Decimal('0.00'), credit_limit - current_balance)
        current_util, _ = calculate_card_utilization(credit_limit, current_balance)
        
        card_info.append({
            "card": card,
            "credit_limit": credit_limit,
            "current_balance": current_balance,
            "available_credit": available_credit,
            "current_utilization": current_util
        })
        
        total_available_credit += available_credit
    
    # Check if allocation is feasible
    if amount > total_available_credit:
        return {
            "allocation_feasible": False,
            "allocation_steps": [],
            "optimization_summary": f"Insufficient credit: need ${amount}, have ${total_available_credit} available",
            "total_available_credit": total_available_credit,
            "warnings": [
                f"Total amount (${amount}) exceeds available credit (${total_available_credit})",
                f"Consider paying down existing balances or requesting a credit limit increase"
            ]
        }
    
    # Sort cards by current utilization (lowest first)
    card_info.sort(key=lambda x: x['current_utilization'])
    
    # Allocation algorithm
    allocation_steps = []
    remaining_amount = amount
    warnings = []
    
    # Target utilization range
    OPTIMAL_MIN = Decimal('10.00')
    OPTIMAL_MAX = Decimal('30.00')
    
    for info in card_info:
        if remaining_amount <= 0:
            break
        
        card = info['card']
        credit_limit = info['credit_limit']
        current_balance = info['current_balance']
        available_credit = info['available_credit']
        current_util = info['current_utilization']
        
        if available_credit <= 0 or credit_limit <= 0:
            continue
        
        # Calculate max charge to stay at or below 30% utilization
        target_balance_at_30 = credit_limit * (OPTIMAL_MAX / 100)
        max_charge_for_optimal = max(Decimal('0.00'), target_balance_at_30 - current_balance)
        
        # Determine how much to charge on this card
        if remaining_amount <= max_charge_for_optimal:
            # Can charge all remaining and stay within optimal range
            charge_amount = remaining_amount
            reason = "Stays within optimal utilization range (10-30%)"
        elif max_charge_for_optimal > 0:
            # Charge up to 30% limit
            charge_amount = min(max_charge_for_optimal, available_credit)
            reason = f"Charged to optimal limit (30%), ${remaining_amount - charge_amount:.2f} remaining"
        else:
            # Already above 30%, use remaining capacity
            charge_amount = min(remaining_amount, available_credit)
            reason = "Already above optimal range, using available credit"
            warnings.append(
                f"{card.issuer} {card.product} is already at {current_util:.1f}% utilization"
            )
        
        new_balance = current_balance + charge_amount
        new_util, _ = calculate_card_utilization(credit_limit, new_balance)
        
        allocation_steps.append(CardPaymentStep(
            card_id=card.id,
            issuer=card.issuer,
            product=card.product,
            last4=card.last4,
            amount_to_charge=charge_amount,
            current_utilization=current_util,
            new_utilization=new_util,
            available_credit=available_credit,
            reason=reason
        ))
        
        remaining_amount -= charge_amount
    
    # Generate optimization summary
    if remaining_amount > Decimal('0.01'):  # Small rounding tolerance
        warnings.append(f"Could not allocate ${remaining_amount:.2f}, insufficient available credit")
        optimization_summary = f"Partial allocation: ${amount - remaining_amount:.2f} of ${amount:.2f}"
    else:
        cards_used = len(allocation_steps)
        cards_in_optimal = sum(1 for step in allocation_steps 
                               if OPTIMAL_MIN <= step.new_utilization <= OPTIMAL_MAX)
        
        if cards_in_optimal == cards_used:
            optimization_summary = f"Optimal allocation across {cards_used} card(s), all within 10-30% range"
        else:
            optimization_summary = f"Allocated across {cards_used} card(s), {cards_in_optimal} within optimal range"
    
    return {
        "allocation_feasible": remaining_amount < Decimal('0.01'),
        "allocation_steps": allocation_steps,
        "optimization_summary": optimization_summary,
        "total_available_credit": total_available_credit,
        "warnings": warnings
    }
