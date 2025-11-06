"""
File upload and statement management API endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from loguru import logger

from app.core.db import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, Statement, Transaction
from app.services.storage import StorageService
from app.services.quota import QuotaService, QuotaExceeded
from app.services.parser import StatementParser
from app.schemas.files import (
    UploadResponse,
    StatementResponse,
    StatementListResponse,
    StatementStatusResponse
)


router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a statement file (PDF, CSV, or image)
    
    - Validates file type and size
    - Checks statement quota
    - Saves to user-specific storage directory
    - Creates Statement record with parsed=False
    - Parses immediately and increments quota
    """
    try:
        # Check statement quota BEFORE uploading
        try:
            QuotaService.check_statement_quota(db, current_user, current_user.locale)
        except QuotaExceeded as qe:
            raise HTTPException(status_code=402, detail={
                "message": qe.message,
                "upgrade_tier": qe.upgrade_tier,
                "type": "statement_quota_exceeded"
            })
        # Save file to storage
        file_path, file_size, source_type = await StorageService.save_upload(
            file,
            current_user.id
        )
        
        # Create Statement record
        statement = Statement(
            user_id=current_user.id,
            source_type=source_type,
            file_path=file_path,
            parsed=False
        )
        db.add(statement)
        db.commit()
        db.refresh(statement)
        
        logger.info(
            f"User {current_user.id} uploaded statement {statement.id}: "
            f"{file.filename} ({source_type})"
        )
        
        # Parse statement immediately
        message = "File uploaded successfully."
        try:
            txn_count = StatementParser.parse_statement(statement, db)
            
            # Only increment quota after successful parsing
            QuotaService.increment_statements_parsed(db, current_user)
            QuotaService.increment_files_parsed(db, current_user)  # Legacy
            
            message = f"File uploaded and parsed successfully. {txn_count} transactions created."
        except Exception as e:
            logger.error(f"Parsing failed for statement {statement.id}: {e}")
            message = f"File uploaded but parsing failed. You can retry parsing later."
        
        return UploadResponse(
            statement_id=statement.id,
            filename=file.filename,
            size_bytes=file_size,
            source_type=source_type,
            message=message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.get("/statements", response_model=StatementListResponse)
def list_statements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all statements for the current user
    
    Returns paginated list of statements with their status
    """
    # Get total count
    total = db.query(func.count(Statement.id)).filter(
        Statement.user_id == current_user.id
    ).scalar()
    
    # Get paginated statements
    statements = db.query(Statement).filter(
        Statement.user_id == current_user.id
    ).order_by(
        Statement.created_at.desc()
    ).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return StatementListResponse(
        statements=[StatementResponse.model_validate(s) for s in statements],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/statements/{statement_id}", response_model=StatementStatusResponse)
def get_statement_status(
    statement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get parsing status of a specific statement
    
    Returns:
        - parsed: Whether statement has been parsed
        - transaction_count: Number of transactions extracted
        - error: Error message if parsing failed
    """
    statement = db.query(Statement).filter(
        Statement.id == statement_id,
        Statement.user_id == current_user.id
    ).first()
    
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    # Count transactions from this statement
    transaction_count = db.query(func.count(Transaction.id)).filter(
        Transaction.user_id == current_user.id
        # TODO: Add statement_id to Transaction model to link them
        # Transaction.statement_id == statement_id
    ).scalar()
    
    return StatementStatusResponse(
        id=statement.id,
        parsed=statement.parsed,
        transaction_count=transaction_count,
        error=None,  # TODO: Add error field to Statement model
        created_at=statement.created_at,
        updated_at=statement.updated_at
    )


@router.delete("/statements/{statement_id}")
def delete_statement(
    statement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a statement and its associated file
    
    Note: This does NOT delete transactions that were extracted from it.
    To delete transactions, use the transactions API.
    """
    statement = db.query(Statement).filter(
        Statement.id == statement_id,
        Statement.user_id == current_user.id
    ).first()
    
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    # Delete file from storage
    StorageService.delete_file(statement.file_path)
    
    # Delete statement record
    db.delete(statement)
    db.commit()
    
    logger.info(f"User {current_user.id} deleted statement {statement_id}")
    
    return {
        "message": "Statement deleted successfully",
        "statement_id": statement_id
    }


@router.post("/statements/{statement_id}/reparse")
def reparse_statement(
    statement_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Re-parse a statement with optional custom column mapping
    
    TODO: Accept mapping overrides for CSV files
    TODO: Enqueue background task to reparse
    """
    statement = db.query(Statement).filter(
        Statement.id == statement_id,
        Statement.user_id == current_user.id
    ).first()
    
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    # Reset parsed status
    statement.parsed = False
    db.commit()
    
    # TODO: Enqueue parsing task with custom mapping
    # from app.workers.parser import parse_statement_task
    # parse_statement_task.delay(statement.id, mapping=custom_mapping)
    
    logger.info(f"User {current_user.id} requested reparse of statement {statement_id}")
    
    return {
        "message": "Statement will be re-parsed shortly",
        "statement_id": statement_id
    }
