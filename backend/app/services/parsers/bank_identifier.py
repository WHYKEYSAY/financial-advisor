"""
Bank and account type identifier for statement parsing
"""
import re
from typing import Optional, Tuple
from loguru import logger


class BankIdentifier:
    """Identifies bank/institution and account type from statement content"""
    
    # Bank identification patterns
    BANK_PATTERNS = {
        "CIBC": [
            r"CIBC.*Account Statement",
            r"cibc\.com",
            r"CIBC Royal Bank",
        ],
        "RBC": [
            r"RBC.*Visa",
            r"Royal Bank.*Canada",
            r"rbcroyalbank\.com",
            r"RBC Avion",
        ],
        "MBNA": [
            r"MBNA.*Mastercard",
            r"mbna\.ca",
            r"TD MBNA",
        ],
        "PC Financial": [
            r"President'?s Choice Financial",
            r"PC.*Mastercard",
            r"pcfinancial\.ca",
            r"PC Optimum",
        ],
        "TD": [
            r"TD.*Bank",
            r"td\.com",
        ],
        "Scotiabank": [
            r"Scotiabank",
            r"scotiabank\.com",
        ],
        "BMO": [
            r"Bank of Montreal",
            r"BMO.*Mastercard",
            r"bmo\.com",
        ],
    }
    
    # Account type patterns
    ACCOUNT_TYPE_PATTERNS = {
        "credit_card": [
            r"Credit Card",
            r"Mastercard",
            r"Visa",
            r"American Express",
            r"Amex",
            r"Card.*Statement",
            r"Annual Fee",
            r"Purchases.*Cash Advances",
        ],
        "checking": [
            r"Chequing.*Account",
            r"Checking.*Account",
            r"Transaction.*Account",
            r"Current.*Account",
        ],
        "savings": [
            r"Savings.*Account",
            r"TFSA",
            r"RRSP",
        ],
    }
    
    @staticmethod
    def identify(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Identify bank, account type, and account number from statement text
        
        Args:
            text: Full text content of the statement
            
        Returns:
            (institution, account_type, account_number)
        """
        text_lower = text.lower()
        
        # Identify bank/institution
        institution = None
        for bank, patterns in BankIdentifier.BANK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    institution = bank
                    break
            if institution:
                break
        
        # Identify account type
        account_type = None
        for acc_type, patterns in BankIdentifier.ACCOUNT_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    account_type = acc_type
                    break
            if account_type:
                break
        
        # Extract account/card number (last 4 digits)
        account_number = None
        # Common patterns for card/account numbers
        number_patterns = [
            # Credit cards
            r'(?:\*{4}|\d{4})\s+(?:\d{2}\*{2})\s+\*{4}\s+(\d{4})',  # 4514 01** **** 0712
            r'\*{4}[\s-]+\*{4}[\s-]+\*{4}[\s-]+(\d{4})',  # **** **** **** 1234
            r'[X]{4}[\s-]+[X]{4}[\s-]+[X]{4}[\s-]+(\d{4})',  # XXXX XXXX XXXX 1234
            r'\d{4}[\s-]+\*{4}[\s-]+\*{4}[\s-]+(\d{4})',  # 1234 **** **** 5678
            r'Card.*?ending.*?(\d{4})',  # Card ending in 1234
            r'Card.*?number.*?\*+(\d{4})',  # Card number ****1234
            # Bank accounts
            r'Account[\s#:]+.*?(\d{4})(?!\d)',  # Account: 1234 or Account #1234
            r'Account ending.*?(\d{4})',  # Account ending in 1234
            r'[Aa]cct.*?(\d{4})(?!\d)',  # Acct 1234
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, text)
            if match:
                account_number = match.group(1) if match.lastindex else match.group(0)
                break
        
        logger.debug(
            f"Identified: institution={institution}, "
            f"account_type={account_type}, "
            f"account_number={account_number}"
        )
        
        return institution, account_type, account_number
