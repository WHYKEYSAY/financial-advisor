"""
Image OCR parser using pytesseract
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger


class ImageParser:
    """Parser for image statement files using OCR"""
    
    @staticmethod
    def preprocess_image(image_path: str) -> Image.Image:
        """
        Preprocess image for better OCR results
        - Convert to grayscale
        - Enhance contrast
        - Apply denoising
        """
        try:
            img = Image.open(image_path)
            
            # Convert to grayscale
            img = img.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)
            
            # Sharpen
            img = img.filter(ImageFilter.SHARPEN)
            
            # Threshold (binarize)
            threshold = 128
            img = img.point(lambda p: 255 if p > threshold else 0)
            
            return img
            
        except Exception as e:
            logger.error(f"Failed to preprocess image {image_path}: {e}")
            # Return original if preprocessing fails
            return Image.open(image_path)
    
    @staticmethod
    def extract_text_with_ocr(image_path: str, languages: str = 'eng+chi_sim') -> str:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to image file
            languages: Tesseract language codes (e.g., 'eng', 'eng+chi_sim')
        """
        try:
            # Preprocess image
            img = ImageParser.preprocess_image(image_path)
            
            # Perform OCR
            # Configure tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6'  # LSTM engine, assume uniform text block
            
            text = pytesseract.image_to_string(
                img,
                lang=languages,
                config=custom_config
            )
            
            logger.info(f"OCR extracted {len(text)} characters from {image_path}")
            return text
            
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            raise ValueError(f"OCR extraction failed: {str(e)}")
    
    @staticmethod
    def parse_date_from_text(text: str) -> Optional[datetime]:
        """Extract and parse date from OCR text"""
        # Date patterns
        patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{2}/\d{2}/\d{4}\b',
            r'\b\d{2}-\d{2}-\d{4}\b',
            r'\b[A-Za-z]{3}\s+\d{1,2},?\s+\d{4}\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(0)
                
                formats = [
                    "%Y-%m-%d",
                    "%m/%d/%Y",
                    "%d-%m-%Y",
                    "%b %d, %Y",
                    "%b %d %Y",
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
        
        return None
    
    @staticmethod
    def parse_amount_from_text(text: str) -> Optional[float]:
        """Extract and parse amount from OCR text"""
        # Amount patterns (allowing for OCR errors)
        patterns = [
            r'[\$]?\s*-?\d{1,3}(?:,?\d{3})*\.?\d{0,2}',
            r'\(\s*[\$]?\s*\d{1,3}(?:,?\d{3})*\.?\d{0,2}\s*\)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean up
                amount_str = match.replace('$', '').replace(',', '').replace(' ', '')
                
                # Handle parentheses
                is_negative = False
                if amount_str.startswith('(') and amount_str.endswith(')'):
                    amount_str = amount_str[1:-1]
                    is_negative = True
                
                try:
                    amount = float(amount_str)
                    # Filter out obviously wrong values
                    if 0.01 <= abs(amount) <= 1000000:
                        return -amount if is_negative else amount
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def parse(file_path: str) -> List[Dict]:
        """
        Parse image file using OCR and extract transactions
        
        Note: OCR accuracy depends on:
        - Image quality (resolution, clarity)
        - Text orientation (should be upright)
        - Font type and size
        - Language support
        
        For production, consider:
        - Image deskewing
        - Multiple OCR engines
        - ML-based post-processing
        """
        try:
            logger.info(f"Parsing image with OCR: {file_path}")
            
            # Extract text using OCR
            text = ImageParser.extract_text_with_ocr(file_path)
            
            if not text.strip():
                logger.warning(f"No text extracted from image {file_path}")
                return []
            
            # Split text into lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            transactions = []
            
            # Try to parse transactions from lines
            # This is a simple heuristic approach
            for line in lines:
                # Skip header-like lines
                if any(keyword in line.lower() for keyword in ['date', 'description', 'amount', 'statement', 'account']):
                    continue
                
                # Try to extract date and amount from line
                date = ImageParser.parse_date_from_text(line)
                amount = ImageParser.parse_amount_from_text(line)
                
                if date and amount is not None:
                    # Use the line as description, removing date and amount patterns
                    description = re.sub(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b', '', line)
                    description = re.sub(r'[\$]?\s*-?\d{1,3}(?:,?\d{3})*\.?\d{0,2}', '', description)
                    description = description.strip()
                    
                    transaction = {
                        "date": date,
                        "amount": amount,
                        "description": description,
                        "currency": "CAD",
                        "raw_data": {"ocr_line": line}
                    }
                    
                    transactions.append(transaction)
            
            logger.info(f"Parsed {len(transactions)} transactions from image via OCR")
            
            if not transactions:
                logger.warning(
                    f"No transactions found in image. Possible issues:\n"
                    f"  - Image quality too low\n"
                    f"  - Text orientation incorrect\n"
                    f"  - OCR language mismatch\n"
                    f"  - Statement format not recognized\n"
                    f"OCR output preview: {text[:200]}..."
                )
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to parse image {file_path}: {e}")
            raise ValueError(f"Image OCR parsing failed: {str(e)}")
