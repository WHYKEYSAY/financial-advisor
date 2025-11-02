"""
Merchant normalization and transaction categorization service
"""
import json
from pathlib import Path
from typing import Optional, Tuple, Dict
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
from loguru import logger

from app.models.models import Merchant, Transaction
from app.services.quota import QuotaService


class CategorizationService:
    """Service for normalizing merchants and categorizing transactions"""
    
    # Standard categories
    CATEGORIES = [
        "groceries",
        "dining",
        "subscription",
        "transport",
        "rent",
        "travel",
        "utilities",
        "pharmacy",
        "gas",
        "entertainment",
        "shopping",
        "other"
    ]
    
    # Confidence thresholds
    FUZZY_MATCH_THRESHOLD = 80  # Out of 100
    AI_FALLBACK_THRESHOLD = 60   # Use AI if below this
    
    def __init__(self):
        """Initialize with merchant aliases data"""
        self._aliases_data = None
        self._alias_to_merchant = None
        self.load_aliases()
    
    def load_aliases(self):
        """Load merchant aliases from JSON file"""
        try:
            aliases_path = Path(__file__).parent.parent / "data" / "merchant_aliases.json"
            
            with open(aliases_path, 'r', encoding='utf-8') as f:
                self._aliases_data = json.load(f)
            
            # Build reverse lookup: alias -> merchant key
            self._alias_to_merchant = {}
            for merchant_key, data in self._aliases_data.items():
                # Add canonical name
                canonical_lower = data["canonical"].lower()
                self._alias_to_merchant[canonical_lower] = merchant_key
                
                # Add all aliases
                for alias in data["aliases"]:
                    self._alias_to_merchant[alias.lower()] = merchant_key
            
            logger.info(f"Loaded {len(self._aliases_data)} merchant patterns with {len(self._alias_to_merchant)} aliases")
            
        except Exception as e:
            logger.error(f"Failed to load merchant aliases: {e}")
            self._aliases_data = {}
            self._alias_to_merchant = {}
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for matching"""
        if not text:
            return ""
        
        # Lowercase
        text = text.lower().strip()
        
        # Remove common noise
        noise_words = [
            '#', '*', '-', '_', 'payment', 'purchase', 'pos', 'debit', 'credit',
            'visa', 'mastercard', 'online', 'www.', '.com', '.ca', '.net'
        ]
        
        for noise in noise_words:
            text = text.replace(noise, ' ')
        
        # Collapse multiple spaces
        text = ' '.join(text.split())
        
        return text
    
    def match_merchant_fuzzy(self, raw_merchant: str) -> Optional[Tuple[str, str, int]]:
        """
        Match merchant using fuzzy string matching
        
        Returns:
            (canonical_name, category, confidence_score) or None
        """
        if not raw_merchant or not self._alias_to_merchant:
            return None
        
        normalized = self.normalize_text(raw_merchant)
        
        if not normalized:
            return None
        
        # Try exact match first
        if normalized in self._alias_to_merchant:
            merchant_key = self._alias_to_merchant[normalized]
            data = self._aliases_data[merchant_key]
            return data["canonical"], data["category"], 100
        
        # Fuzzy match against all aliases
        best_match = process.extractOne(
            normalized,
            self._alias_to_merchant.keys(),
            scorer=fuzz.ratio
        )
        
        if best_match and best_match[1] >= self.FUZZY_MATCH_THRESHOLD:
            matched_alias = best_match[0]
            merchant_key = self._alias_to_merchant[matched_alias]
            data = self._aliases_data[merchant_key]
            
            logger.debug(
                f"Fuzzy matched '{raw_merchant}' -> '{data['canonical']}' "
                f"(confidence: {best_match[1]})"
            )
            
            return data["canonical"], data["category"], best_match[1]
        
        return None
    
    def get_or_create_merchant(
        self,
        db: Session,
        canonical_name: str,
        raw_merchant: str
    ) -> Merchant:
        """Get or create a Merchant record"""
        # Check if merchant exists
        merchant = db.query(Merchant).filter(
            Merchant.canonical_name == canonical_name
        ).first()
        
        if merchant:
            # Update aliases if raw_merchant is new
            aliases = merchant.aliases or []
            raw_lower = raw_merchant.lower()
            
            if raw_lower not in [a.lower() for a in aliases]:
                aliases.append(raw_merchant)
                merchant.aliases = aliases
                db.commit()
                db.refresh(merchant)
            
            return merchant
        
        # Create new merchant
        merchant = Merchant(
            canonical_name=canonical_name,
            aliases=[raw_merchant]
        )
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        
        logger.info(f"Created new merchant: {canonical_name}")
        return merchant
    
    def categorize_transaction(
        self,
        transaction: Transaction,
        db: Session
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Categorize a transaction and normalize its merchant
        
        Returns:
            (canonical_merchant_name, category)
        """
        if not transaction.raw_merchant:
            return None, "other"
        
        # Try fuzzy matching
        match_result = self.match_merchant_fuzzy(transaction.raw_merchant)
        
        if match_result:
            canonical_name, category, confidence = match_result
            
            # Get or create merchant
            merchant = self.get_or_create_merchant(db, canonical_name, transaction.raw_merchant)
            
            # Update transaction
            transaction.merchant_id = merchant.id
            transaction.category = category
            
            logger.debug(
                f"Transaction {transaction.id}: '{transaction.raw_merchant}' -> "
                f"'{canonical_name}' ({category}) [confidence: {confidence}]"
            )
            
            return canonical_name, category
        
        # No match found - try AI fallback
        logger.debug(f"No fuzzy match for merchant: {transaction.raw_merchant}, trying AI...")
        
        try:
            # Import here to avoid circular dependency
            from app.services.ai import ai_service
            from app.models.models import User
            
            # Get user for quota check
            user = db.query(User).filter(User.id == transaction.user_id).first()
            if not user:
                transaction.category = "other"
                return None, "other"
            
            # Check AI quota
            try:
                QuotaService.check_ai_quota(db, user, user.locale)
            except Exception as quota_error:
                # Quota exceeded, use fallback
                logger.warning(f"AI quota exceeded for user {user.id}: {quota_error}")
                transaction.category = "other"
                return None, "other"
            
            # Use AI for normalization and categorization
            canonical_name, confidence = ai_service.normalize_merchant(
                transaction.raw_merchant,
                transaction.amount,
                user.locale
            )
            
            category, subcategory, cat_confidence = ai_service.categorize_transaction(
                canonical_name,
                transaction.amount,
                transaction.raw_merchant,
                user.locale
            )
            
            # Create merchant if AI confidence is high enough
            if confidence >= 70:
                merchant = self.get_or_create_merchant(db, canonical_name, transaction.raw_merchant)
                transaction.merchant_id = merchant.id
            
            transaction.category = category
            if subcategory:
                transaction.subcategory = subcategory
            
            # Increment AI quota
            QuotaService.increment_ai_calls(db, user, count=2)  # 2 calls: normalize + categorize
            
            logger.info(
                f"AI processed transaction {transaction.id}: '{transaction.raw_merchant}' -> "
                f"'{canonical_name}' ({category}) [confidence: {cat_confidence}]"
            )
            
            return canonical_name, category
            
        except Exception as e:
            logger.error(f"AI fallback failed: {e}")
            transaction.category = "other"
            return None, "other"
    
    def batch_categorize(
        self,
        db: Session,
        user_id: int,
        limit: int = 100
    ) -> int:
        """
        Batch categorize uncategorized transactions for a user
        
        Returns:
            Number of transactions categorized
        """
        # Get uncategorized transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.category == None
        ).limit(limit).all()
        
        if not transactions:
            logger.info(f"No uncategorized transactions for user {user_id}")
            return 0
        
        categorized_count = 0
        
        for txn in transactions:
            try:
                self.categorize_transaction(txn, db)
                categorized_count += 1
            except Exception as e:
                logger.error(f"Failed to categorize transaction {txn.id}: {e}")
        
        db.commit()
        
        logger.info(
            f"Categorized {categorized_count}/{len(transactions)} transactions "
            f"for user {user_id}"
        )
        
        return categorized_count
    
    def get_category_breakdown(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, float]:
        """Get spending breakdown by category"""
        from sqlalchemy import func
        
        result = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.category != None
        ).group_by(
            Transaction.category
        ).all()
        
        breakdown = {cat: float(total) for cat, total in result}
        return breakdown


# Global instance
categorization_service = CategorizationService()
