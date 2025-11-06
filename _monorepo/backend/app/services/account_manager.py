"""
Account and Card management service
"""
from typing import Optional, Union
from sqlalchemy.orm import Session
from loguru import logger

from app.models.models import User, Account, Card, Statement


class AccountManager:
    """Service for managing user accounts and cards"""
    
    @staticmethod
    def get_or_create_account(
        db: Session,
        user: User,
        institution: str,
        account_type: str,
        mask: Optional[str] = None
    ) -> Account:
        """
        Get or create a bank account record
        
        Args:
            db: Database session
            user: User owning the account
            institution: Bank name (CIBC, RBC, etc.)
            account_type: checking, savings
            mask: Last 4 digits of account number
        
        Returns:
            Account record
        """
        # Try to find existing account
        query = db.query(Account).filter(
            Account.user_id == user.id,
            Account.institution == institution,
            Account.account_type == account_type
        )
        
        if mask:
            query = query.filter(Account.mask == mask)
        
        account = query.first()
        
        if account:
            logger.debug(f"Found existing account: {institution} {account_type} {mask}")
            return account
        
        # Create new account
        account = Account(
            user_id=user.id,
            institution=institution,
            account_type=account_type,
            mask=mask,
            is_active=True
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        
        logger.info(f"Created account: {institution} {account_type} {mask} for user {user.id}")
        return account
    
    @staticmethod
    def get_or_create_card(
        db: Session,
        user: User,
        issuer: str,
        product: str,
        last4: Optional[str] = None
    ) -> Card:
        """
        Get or create a credit card record
        
        Args:
            db: Database session
            user: User owning the card
            issuer: Card issuer (MBNA, RBC, PC Financial, etc.)
            product: Card product name (Mastercard, Visa, etc.)
            last4: Last 4 digits of card number
        
        Returns:
            Card record
        """
        # Try to find existing card
        query = db.query(Card).filter(
            Card.user_id == user.id,
            Card.issuer == issuer,
            Card.product == product
        )
        
        if last4:
            query = query.filter(Card.last4 == last4)
        
        card = query.first()
        
        if card:
            logger.debug(f"Found existing card: {issuer} {product} {last4}")
            return card
        
        # Create new card
        card = Card(
            user_id=user.id,
            issuer=issuer,
            product=product,
            last4=last4,
            is_active=True
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        
        logger.info(f"Created card: {issuer} {product} {last4} for user {user.id}")
        return card
    
    @staticmethod
    def link_statement_to_account(
        db: Session,
        statement: Statement,
        user: User
    ) -> Union[Account, Card, None]:
        """
        Link a statement to its corresponding Account or Card
        
        Args:
            db: Database session
            statement: Statement to link
            user: User owning the statement
        
        Returns:
            Account or Card record, or None if linking failed
        """
        if not statement.institution or not statement.account_type:
            logger.warning(f"Statement {statement.id} missing institution or account_type")
            return None
        
        # Extract last 4 digits
        mask = statement.account_number
        
        if statement.account_type == "credit_card":
            # Create/get Card
            # Determine product type from institution
            product = "Mastercard"  # Default
            if statement.institution in ["RBC"]:
                product = "Visa"
            elif statement.institution in ["MBNA", "PC Financial"]:
                product = "Mastercard"
            
            card = AccountManager.get_or_create_card(
                db,
                user,
                issuer=statement.institution,
                product=product,
                last4=mask
            )
            return card
        
        else:
            # Create/get Account (checking/savings)
            account = AccountManager.get_or_create_account(
                db,
                user,
                institution=statement.institution,
                account_type=statement.account_type,
                mask=mask
            )
            return account
