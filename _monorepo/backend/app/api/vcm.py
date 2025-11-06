"""
VCM (Virtual Credit Manager) API endpoints

Provides credit card management functionality:
- Credit limit overview
- Utilization tracking
- Card management
- Payment reminders
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.core.db import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, Card
from app.schemas.vcm import (
    CreditOverviewResponse,
    UtilizationResponse,
    CardSummary,
    AddCardRequest,
    AddCardResponse,
    PaymentReminderResponse,
    SpendingAllocationRequest,
    SpendingAllocationResponse
)
from app.services.credit_manager import (
    get_credit_overview,
    get_card_summary,
    get_payment_reminders,
    optimize_spending_allocation
)


router = APIRouter(prefix="/vcm", tags=["VCM"])


@router.get("/overview", response_model=CreditOverviewResponse)
def get_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get complete credit overview across all cards.
    
    Returns:
    - Total credit limit
    - Total used credit
    - Overall utilization rate
    - Overall health status
    - Per-card summaries with utilization
    
    **Response Example:**
    ```json
    {
      "total_credit_limit": 25000.00,
      "total_used": 5000.00,
      "overall_utilization": 20.00,
      "health_status": "optimal",
      "cards_summary": [...]
    }
    ```
    
    **Health Status Zones:**
    - `optimal`: 10-30% utilization
    - `underutilized`: <10% utilization
    - `elevated`: 30-50% utilization
    - `high`: >50% utilization
    """
    try:
        overview = get_credit_overview(db, current_user.id)
        return overview
    except Exception as e:
        logger.error(f"Error getting credit overview for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit overview"
        )


@router.get("/utilization", response_model=UtilizationResponse)
def get_utilization(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get credit utilization analysis.
    
    Returns overall utilization rate and per-card breakdown.
    
    **Response Example:**
    ```json
    {
      "overall_utilization": 20.00,
      "health_status": "optimal",
      "per_card": [
        {
          "card_id": 1,
          "issuer": "RBC",
          "product": "Avion Visa Infinite",
          "credit_limit": 10000.00,
          "current_balance": 2000.00,
          "utilization_rate": 20.00,
          "health_status": "optimal",
          "last4": "1234"
        }
      ]
    }
    ```
    """
    try:
        overview = get_credit_overview(db, current_user.id)
        
        return UtilizationResponse(
            overall_utilization=overview.overall_utilization,
            health_status=overview.health_status,
            per_card=overview.cards_summary
        )
    except Exception as e:
        logger.error(f"Error getting utilization for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve utilization data"
        )


@router.get("/cards/{card_id}/utilization", response_model=CardSummary)
def get_card_utilization(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get utilization data for a specific credit card.
    
    **Path Parameters:**
    - `card_id`: ID of the credit card
    
    **Returns:**
    Card summary including:
    - Credit limit
    - Current balance
    - Utilization rate
    - Health status
    
    **Errors:**
    - `404`: Card not found or doesn't belong to current user
    """
    try:
        card_data = get_card_summary(db, card_id, current_user.id)
        
        if not card_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID {card_id} not found or access denied"
            )
        
        return card_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting card {card_id} utilization for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve card utilization"
        )


@router.post("/cards", response_model=AddCardResponse, status_code=status.HTTP_201_CREATED)
def add_card(
    card_data: AddCardRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new credit card to the user's account.
    
    **Request Body:**
    ```json
    {
      "issuer": "RBC",
      "product": "Avion Visa Infinite",
      "credit_limit": 10000.00,
      "last4": "1234",
      "statement_day": 15,
      "due_day": 5
    }
    ```
    
    **Required Fields:**
    - `issuer`: Card issuer (e.g., RBC, MBNA, CIBC)
    - `product`: Card product name
    - `credit_limit`: Credit limit (must be > 0)
    
    **Optional Fields:**
    - `last4`: Last 4 digits of card number
    - `statement_day`: Day of month for statement (1-31)
    - `due_day`: Day of month for payment due date (1-31)
    
    **Returns:**
    - Created card information
    
    **Errors:**
    - `400`: Invalid input (e.g., credit_limit <= 0)
    """
    try:
        # Create new card
        new_card = Card(
            user_id=current_user.id,
            issuer=card_data.issuer,
            product=card_data.product,
            credit_limit=card_data.credit_limit,
            last4=card_data.last4,
            statement_day=card_data.statement_day,
            due_day=card_data.due_day,
            is_active=True
        )
        
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        
        logger.info(f"User {current_user.id} added card: {new_card.issuer} {new_card.product} (ID: {new_card.id})")
        
        return AddCardResponse(
            card_id=new_card.id,
            issuer=new_card.issuer,
            product=new_card.product,
            credit_limit=new_card.credit_limit,
            last4=new_card.last4,
            message="Card added successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding card for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add card"
        )


@router.get("/cards", response_model=List[CardSummary])
def list_cards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all credit cards for the current user.
    
    Returns a list of all active credit cards with their current utilization status.
    
    **Response:**
    Array of CardSummary objects, each containing:
    - Card details (issuer, product, last4)
    - Credit limit
    - Current balance
    - Utilization rate
    - Health status
    """
    try:
        overview = get_credit_overview(db, current_user.id)
        return overview.cards_summary
    except Exception as e:
        logger.error(f"Error listing cards for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cards"
        )


@router.get("/reminders", response_model=List[PaymentReminderResponse])
def get_reminders(
    days_ahead: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get payment reminders for upcoming due dates.
    
    Returns cards with payments due within the specified number of days.
    
    **Query Parameters:**
    - `days_ahead`: Number of days to look ahead (default: 7)
    
    **Response:**
    Array of payment reminders, each containing:
    - Card details
    - Due date
    - Days until due
    - Current balance
    - Estimated minimum payment (3% of balance or $10, whichever is greater)
    
    **Note:**
    Only cards with a configured `due_day` will be included.
    """
    try:
        reminders = get_payment_reminders(db, current_user.id, days_ahead)
        return reminders
    except Exception as e:
        logger.error(f"Error getting reminders for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment reminders"
        )


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a credit card (soft delete).
    
    **Path Parameters:**
    - `card_id`: ID of the card to deactivate
    
    **Note:**
    This performs a soft delete by setting `is_active = False`.
    The card and its transaction history are preserved in the database.
    
    **Errors:**
    - `404`: Card not found or doesn't belong to current user
    """
    try:
        card = db.query(Card).filter(
            Card.id == card_id,
            Card.user_id == current_user.id,
            Card.is_active == True
        ).first()
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID {card_id} not found or access denied"
            )
        
        card.is_active = False
        db.commit()
        
        logger.info(f"User {current_user.id} deactivated card {card_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting card {card_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete card"
        )


@router.post("/optimize-spending", response_model=SpendingAllocationResponse)
def optimize_spending(
    request: SpendingAllocationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Optimize spending allocation across multiple credit cards.
    
    **Algorithm:**
    1. Prioritizes cards with lowest utilization
    2. Keeps all cards within optimal range (10-30%) when possible
    3. Avoids pushing any card above 30% utilization
    4. Minimizes number of cards used while maintaining health
    
    **Request Body:**
    ```json
    {
      "amount": 1500.00
    }
    ```
    
    **Response includes:**
    - Step-by-step payment instructions for each card
    - Current and projected utilization rates
    - Optimization summary and strategy
    - Warnings if allocation pushes cards above optimal range
    
    **Example Response:**
    ```json
    {
      "total_amount": 1500.00,
      "allocation_feasible": true,
      "allocation_steps": [
        {
          "card_id": 1,
          "issuer": "RBC",
          "product": "Avion Visa Infinite",
          "amount_to_charge": 800.00,
          "current_utilization": 15.00,
          "new_utilization": 23.00,
          "reason": "Lowest utilization, stays within optimal range"
        }
      ],
      "optimization_summary": "Allocated across 2 cards, all within 10-30% range",
      "total_available_credit": 15000.00,
      "warnings": []
    }
    ```
    
    **Use Cases:**
    - Planning a large purchase
    - Maintaining optimal credit utilization
    - Splitting payments to minimize credit score impact
    
    **Errors:**
    - `400`: Invalid amount (must be > 0)
    - `400`: Insufficient available credit
    """
    try:
        result = optimize_spending_allocation(db, current_user.id, request.amount)
        
        return SpendingAllocationResponse(
            total_amount=request.amount,
            allocation_feasible=result['allocation_feasible'],
            allocation_steps=result['allocation_steps'],
            optimization_summary=result['optimization_summary'],
            total_available_credit=result['total_available_credit'],
            warnings=result.get('warnings', [])
        )
    except Exception as e:
        logger.error(f"Error optimizing spending for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize spending allocation"
        )
