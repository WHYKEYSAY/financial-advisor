"""
CSV statement parser
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger


class CSVParser:
    """Parser for CSV statement files"""
    
    # Common column name mappings
    COLUMN_MAPPINGS = {
        "date": ["date", "transaction date", "posted date", "trans date", "transaction_date", "post_date"],
        "description": ["description", "merchant", "payee", "memo", "details", "transaction_description"],
        "amount": ["amount", "transaction amount", "debit", "credit", "value", "trans_amount"],
        "currency": ["currency", "ccy", "curr"],
    }
    
    @staticmethod
    def detect_delimiter(file_path: str) -> str:
        """Detect CSV delimiter"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
            
        # Check for common delimiters
        for delim in [',', ';', '\t', '|']:
            if delim in first_line:
                return delim
        
        return ','  # Default to comma
    
    @staticmethod
    def normalize_column_name(col: str) -> str:
        """Normalize column name to lowercase and remove special chars"""
        return col.lower().strip().replace('_', ' ')
    
    @staticmethod
    def find_column(df: pd.DataFrame, target: str) -> Optional[str]:
        """Find column by matching against known aliases"""
        normalized_cols = {CSVParser.normalize_column_name(col): col for col in df.columns}
        
        # Try to match against known aliases
        for alias in CSVParser.COLUMN_MAPPINGS.get(target, []):
            if alias in normalized_cols:
                return normalized_cols[alias]
        
        return None
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format attempts"""
        if pd.isna(date_str):
            return None
        
        # Common date formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d %b %Y",
            "%d %B %Y",
        ]
        
        date_str = str(date_str).strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try pandas parsing as fallback
        try:
            return pd.to_datetime(date_str)
        except:
            logger.warning(f"Failed to parse date: {date_str}")
            return None
    
    @staticmethod
    def parse_amount(amount_str: str) -> Optional[float]:
        """Parse amount string, handling currency symbols and formatting"""
        if pd.isna(amount_str):
            return None
        
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols
        amount_str = amount_str.replace('$', '').replace('€', '').replace('£', '')
        amount_str = amount_str.replace('CAD', '').replace('USD', '').replace('CNY', '')
        
        # Remove commas and spaces
        amount_str = amount_str.replace(',', '').replace(' ', '')
        
        # Handle parentheses as negative
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            logger.warning(f"Failed to parse amount: {amount_str}")
            return None
    
    @staticmethod
    def parse(
        file_path: str,
        custom_mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict]:
        """
        Parse CSV file and extract transactions
        
        Args:
            file_path: Path to CSV file
            custom_mapping: Optional custom column mapping
                           e.g., {"date": "Trans Date", "amount": "Value"}
        
        Returns:
            List of transaction dictionaries
        """
        try:
            # Detect delimiter
            delimiter = CSVParser.detect_delimiter(file_path)
            
            # Read CSV
            df = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding='utf-8-sig',
                skip_blank_lines=True
            )
            
            # Skip empty rows
            df = df.dropna(how='all')
            
            if df.empty:
                logger.warning(f"CSV file is empty: {file_path}")
                return []
            
            logger.info(f"Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")
            
            # Find columns using custom mapping or auto-detection
            col_map = {}
            
            if custom_mapping:
                col_map = custom_mapping
            else:
                # Auto-detect columns
                for target in ["date", "description", "amount", "currency"]:
                    found_col = CSVParser.find_column(df, target)
                    if found_col:
                        col_map[target] = found_col
            
            # Validate required columns
            if "date" not in col_map or "amount" not in col_map:
                raise ValueError(
                    f"Could not find required columns (date, amount). "
                    f"Available columns: {list(df.columns)}"
                )
            
            # Extract transactions
            transactions = []
            
            for idx, row in df.iterrows():
                # Parse date
                date = CSVParser.parse_date(row[col_map["date"]])
                if not date:
                    continue
                
                # Parse amount
                amount = CSVParser.parse_amount(row[col_map["amount"]])
                if amount is None:
                    continue
                
                # Get description
                description = ""
                if "description" in col_map:
                    description = str(row[col_map["description"]]).strip()
                
                # Get currency
                currency = "CAD"  # Default
                if "currency" in col_map and not pd.isna(row[col_map["currency"]]):
                    currency = str(row[col_map["currency"]]).strip().upper()
                
                transaction = {
                    "date": date,
                    "amount": amount,
                    "description": description,
                    "currency": currency,
                    "raw_data": row.to_dict()
                }
                
                transactions.append(transaction)
            
            logger.info(f"Parsed {len(transactions)} transactions from CSV")
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to parse CSV {file_path}: {e}")
            raise ValueError(f"CSV parsing failed: {str(e)}")
