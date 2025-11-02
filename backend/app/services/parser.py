"""
Statement parser service - orchestrates CSV, PDF, and image parsers
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.models.models import Statement, Transaction, User, Merchant
from app.services.parsers.csv_parser import CSVParser
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.image_parser import ImageParser
from app.services.categorization import categorization_service


class StatementParser:
    """Main service for parsing statement files and creating transactions"""
    
    @staticmethod
    def parse_statement(
        statement: Statement,
        db: Session,
        custom_mapping: Optional[Dict[str, str]] = None
    ) -> int:
        """
        Parse a statement file and create Transaction records
        
        Args:
            statement: Statement model instance
            db: Database session
            custom_mapping: Optional custom column mapping for CSV files
        
        Returns:
            Number of transactions created
        """
        try:
            logger.info(f"Parsing statement {statement.id} (type: {statement.source_type})")
            
            # Select parser based on source type
            raw_transactions = []
            
            if statement.source_type == "csv":
                raw_transactions = CSVParser.parse(statement.file_path, custom_mapping)
            elif statement.source_type == "pdf":
                raw_transactions = PDFParser.parse(statement.file_path)
            elif statement.source_type == "image":
                raw_transactions = ImageParser.parse(statement.file_path)
            else:
                raise ValueError(f"Unknown source type: {statement.source_type}")
            
            if not raw_transactions:
                logger.warning(f"No transactions found in statement {statement.id}")
                statement.parsed = True
                db.commit()
                return 0
            
            # Create Transaction records
            transactions_created = 0
            
            for raw_txn in raw_transactions:
                # Check for duplicates (same user, date, amount, description)
                existing = db.query(Transaction).filter(
                    Transaction.user_id == statement.user_id,
                    Transaction.date == raw_txn["date"],
                    Transaction.amount == raw_txn["amount"],
                    Transaction.raw_merchant == raw_txn["description"]
                ).first()
                
                if existing:
                    logger.debug(f"Skipping duplicate transaction: {raw_txn['date']} {raw_txn['amount']}")
                    continue
                
                # Create transaction
                transaction = Transaction(
                    user_id=statement.user_id,
                    date=raw_txn["date"],
                    amount=raw_txn["amount"],
                    currency=raw_txn["currency"],
                    raw_merchant=raw_txn["description"],
                    # Merchant normalization and categorization will be done later
                    merchant_id=None,
                    category=None,
                    subcategory=None,
                    tags=[],
                    meta_data=raw_txn.get("raw_data", {})
                )
                
                db.add(transaction)
                transactions_created += 1
            
            # Commit transactions first
            db.commit()
            
            # Now categorize them
            if transactions_created > 0:
                logger.info(f"Categorizing {transactions_created} transactions...")
                categorization_service.batch_categorize(db, statement.user_id, limit=transactions_created)
            
            # Update statement as parsed
            statement.parsed = True
            
            # Set period dates if we have transactions
            if raw_transactions:
                dates = [t["date"] for t in raw_transactions]
                statement.period_start = min(dates)
                statement.period_end = max(dates)
            
            db.commit()
            
            logger.info(
                f"Statement {statement.id} parsed successfully. "
                f"Created {transactions_created} transactions."
            )
            
            return transactions_created
            
        except Exception as e:
            logger.error(f"Failed to parse statement {statement.id}: {e}")
            statement.parsed = False
            db.commit()
            raise
    
    @staticmethod
    def reparse_statement(
        statement: Statement,
        db: Session,
        custom_mapping: Optional[Dict[str, str]] = None,
        delete_existing: bool = False
    ) -> int:
        """
        Re-parse a statement, optionally deleting existing transactions
        
        Args:
            statement: Statement to reparse
            db: Database session
            custom_mapping: Optional custom column mapping
            delete_existing: Whether to delete existing transactions from this statement
        
        Returns:
            Number of transactions created
        """
        if delete_existing:
            # TODO: Add statement_id to Transaction model to enable this
            # For now, we'll just parse and create new transactions
            logger.warning("Cannot delete existing transactions - statement_id not tracked")
        
        # Reset parsed status
        statement.parsed = False
        db.commit()
        
        # Parse again
        return StatementParser.parse_statement(statement, db, custom_mapping)
    
    @staticmethod
    def get_available_columns(statement: Statement) -> Optional[List[str]]:
        """
        Get available columns from a CSV file for custom mapping
        
        Returns None for non-CSV files
        """
        if statement.source_type != "csv":
            return None
        
        try:
            import pandas as pd
            df = pd.read_csv(statement.file_path, nrows=0)
            return list(df.columns)
        except Exception as e:
            logger.error(f"Failed to read CSV columns from {statement.file_path}: {e}")
            return None
