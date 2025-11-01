"""
PDF statement parser using PyMuPDF
"""
import fitz  # PyMuPDF
import re
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger


class PDFParser:
    """Parser for PDF statement files"""
    
    # Common date patterns
    DATE_PATTERNS = [
        r'\b\d{4}-\d{2}-\d{2}\b',  # 2024-01-15
        r'\b\d{2}/\d{2}/\d{4}\b',  # 01/15/2024
        r'\b\d{2}-\d{2}-\d{4}\b',  # 15-01-2024
        r'\b[A-Za-z]{3}\s+\d{1,2},\s+\d{4}\b',  # Jan 15, 2024
    ]
    
    # Common amount patterns
    AMOUNT_PATTERNS = [
        r'\$?\s*-?\d{1,3}(?:,\d{3})*\.\d{2}',  # $1,234.56 or -1234.56
        r'\(\$?\s*\d{1,3}(?:,\d{3})*\.\d{2}\)',  # ($1,234.56)
    ]
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract all text from PDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
                text += "\n--- PAGE BREAK ---\n"
            
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {e}")
            raise ValueError(f"PDF text extraction failed: {str(e)}")
    
    @staticmethod
    def extract_tables(file_path: str) -> List[List[List[str]]]:
        """
        Extract tables from PDF using text block analysis
        Returns list of tables (pages) containing rows of cells
        """
        try:
            doc = fitz.open(file_path)
            all_tables = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get text blocks with position info
                blocks = page.get_text("blocks")
                
                # Sort blocks by vertical position (top to bottom)
                blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
                
                # Group blocks into rows based on y-coordinate proximity
                rows = []
                current_row = []
                current_y = None
                y_threshold = 5  # pixels
                
                for block in blocks:
                    x0, y0, x1, y1, text, block_no, block_type = block
                    text = text.strip()
                    
                    if not text:
                        continue
                    
                    # Check if this block belongs to current row
                    if current_y is None or abs(y0 - current_y) < y_threshold:
                        current_row.append((x0, text))
                        current_y = y0 if current_y is None else current_y
                    else:
                        # New row
                        if current_row:
                            # Sort cells in row by x position (left to right)
                            current_row = sorted(current_row, key=lambda c: c[0])
                            rows.append([cell[1] for cell in current_row])
                        current_row = [(x0, text)]
                        current_y = y0
                
                # Add last row
                if current_row:
                    current_row = sorted(current_row, key=lambda c: c[0])
                    rows.append([cell[1] for cell in current_row])
                
                all_tables.append(rows)
            
            doc.close()
            return all_tables
            
        except Exception as e:
            logger.error(f"Failed to extract tables from PDF {file_path}: {e}")
            return []
    
    @staticmethod
    def parse_date_from_text(text: str) -> Optional[datetime]:
        """Extract and parse date from text"""
        for pattern in PDFParser.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(0)
                
                # Try to parse with different formats
                formats = [
                    "%Y-%m-%d",
                    "%m/%d/%Y",
                    "%d-%m-%Y",
                    "%b %d, %Y",
                    "%B %d, %Y",
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
        
        return None
    
    @staticmethod
    def parse_amount_from_text(text: str) -> Optional[float]:
        """Extract and parse amount from text"""
        for pattern in PDFParser.AMOUNT_PATTERNS:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(0)
                
                # Clean up
                amount_str = amount_str.replace('$', '').replace(',', '').replace(' ', '')
                
                # Handle parentheses as negative
                is_negative = False
                if amount_str.startswith('(') and amount_str.endswith(')'):
                    amount_str = amount_str[1:-1]
                    is_negative = True
                
                try:
                    amount = float(amount_str)
                    return -amount if is_negative else amount
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def parse(file_path: str) -> List[Dict]:
        """
        Parse PDF file and extract transactions
        
        This is a basic implementation that:
        1. Extracts text and tables from PDF
        2. Looks for transaction patterns
        3. Returns structured transaction data
        
        For production, consider specialized PDF parsing libraries
        or bank-specific parsers for better accuracy.
        """
        try:
            logger.info(f"Parsing PDF: {file_path}")
            
            # Extract tables
            tables = PDFParser.extract_tables(file_path)
            
            if not tables:
                logger.warning(f"No tables found in PDF, falling back to text extraction")
                # Fallback to simple text extraction
                text = PDFParser.extract_text_from_pdf(file_path)
                # TODO: Implement OCR fallback here if needed
                return []
            
            transactions = []
            
            # Process each page's table
            for page_idx, rows in enumerate(tables):
                logger.debug(f"Processing page {page_idx + 1} with {len(rows)} rows")
                
                for row in rows:
                    if len(row) < 2:
                        continue
                    
                    # Try to parse transaction from row
                    # Assume format: [Date, Description, Amount] or similar
                    row_text = " ".join(row)
                    
                    # Extract date
                    date = PDFParser.parse_date_from_text(row_text)
                    if not date:
                        continue
                    
                    # Extract amount
                    amount = PDFParser.parse_amount_from_text(row_text)
                    if amount is None:
                        continue
                    
                    # Get description (cells between date and amount)
                    description = " ".join(row[1:-1]) if len(row) > 2 else row_text
                    description = description.strip()
                    
                    transaction = {
                        "date": date,
                        "amount": amount,
                        "description": description,
                        "currency": "CAD",  # Default, could be extracted from PDF
                        "raw_data": {"row": row, "page": page_idx + 1}
                    }
                    
                    transactions.append(transaction)
            
            logger.info(f"Parsed {len(transactions)} transactions from PDF")
            
            if not transactions:
                logger.warning(
                    f"No transactions found in PDF. This could mean:\n"
                    f"  - PDF format not recognized\n"
                    f"  - OCR might be needed for scanned documents\n"
                    f"  - Custom parser needed for this bank's format"
                )
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise ValueError(f"PDF parsing failed: {str(e)}")
