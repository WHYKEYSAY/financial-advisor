"""
File storage service for handling uploads
"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile
from loguru import logger

from app.core.config import settings


class StorageService:
    """Service for handling file storage operations"""
    
    # Allowed MIME types
    ALLOWED_TYPES = {
        "application/pdf": "pdf",
        "text/csv": "csv",
        "application/vnd.ms-excel": "csv",
        "image/png": "image",
        "image/jpeg": "image",
        "image/jpg": "image",
    }
    
    # Maximum file sizes (in bytes) by type
    MAX_SIZES = {
        "pdf": 25 * 1024 * 1024,      # 25 MB
        "csv": 10 * 1024 * 1024,      # 10 MB
        "image": 15 * 1024 * 1024,    # 15 MB
    }
    
    @staticmethod
    def get_user_upload_dir(user_id: int) -> Path:
        """Get upload directory for a specific user"""
        user_dir = Path(settings.FILE_STORAGE_DIR) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    @staticmethod
    def validate_file_type(content_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file type
        Returns (is_valid, source_type)
        """
        source_type = StorageService.ALLOWED_TYPES.get(content_type)
        if not source_type:
            return False, None
        return True, source_type
    
    @staticmethod
    def validate_file_size(file_size: int, source_type: str) -> bool:
        """Validate file size against limits"""
        max_size = StorageService.MAX_SIZES.get(source_type, settings.max_file_size_bytes)
        return file_size <= max_size
    
    @staticmethod
    def generate_safe_filename(original_filename: str, user_id: int) -> str:
        """
        Generate a safe, unique filename
        Format: timestamp_hash_originalname
        """
        import time
        timestamp = int(time.time())
        
        # Hash the original filename for uniqueness
        file_hash = hashlib.md5(
            f"{user_id}{timestamp}{original_filename}".encode()
        ).hexdigest()[:8]
        
        # Clean original filename
        name = Path(original_filename).stem[:50]  # Limit length
        ext = Path(original_filename).suffix.lower()
        
        # Remove unsafe characters
        safe_name = "".join(c for c in name if c.isalnum() or c in "-_")
        
        return f"{timestamp}_{file_hash}_{safe_name}{ext}"
    
    @staticmethod
    async def save_upload(
        file: UploadFile,
        user_id: int
    ) -> Tuple[str, int, str]:
        """
        Save uploaded file to disk
        
        Returns:
            (file_path, file_size, source_type)
        
        Raises:
            ValueError: If file validation fails
        """
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate content type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        is_valid, source_type = StorageService.validate_file_type(content_type)
        
        if not is_valid:
            raise ValueError(
                f"Invalid file type: {content_type}. "
                f"Allowed types: PDF, CSV, PNG, JPEG"
            )
        
        # Validate file size
        if not StorageService.validate_file_size(file_size, source_type):
            max_mb = StorageService.MAX_SIZES[source_type] / (1024 * 1024)
            raise ValueError(
                f"File too large. Maximum size for {source_type}: {max_mb}MB"
            )
        
        # Generate safe filename
        safe_filename = StorageService.generate_safe_filename(
            file.filename,
            user_id
        )
        
        # Get user directory
        user_dir = StorageService.get_user_upload_dir(user_id)
        file_path = user_dir / safe_filename
        
        # Write file
        try:
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(
                f"Saved file for user {user_id}: {safe_filename} "
                f"({file_size} bytes, type: {source_type})"
            )
            
            return str(file_path), file_size, source_type
            
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            # Clean up partial file if it exists
            if file_path.exists():
                file_path.unlink()
            raise ValueError(f"Failed to save file: {str(e)}")
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "path": str(path),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "exists": True
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
