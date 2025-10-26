"""Transaction routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.config.database import get_db
from app.controllers.transaction_controller import TransactionController
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.transaction import Transaction
from datetime import datetime

router = APIRouter(prefix="/v1", tags=["transactions"])

# Initialize controller
transaction_controller = TransactionController()

# Helper to serialize dates for responses

def _date_to_str(d):
    return d.isoformat() if isinstance(d, datetime) else (d or "")

# Pydantic models
class SMSRequest(BaseModel):
    sms_text: str

class TransactionResponse(BaseModel):
    id: int = None
    vendor: str
    amount: float
    date: str
    category: str
    sms_text: str
    confidence: float

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    vendor: str
    amount: float
    date: str
    category: str
    sms_text: str = None
    confidence: float = 1.0

@router.post("/parse-sms", response_model=TransactionResponse)
async def parse_sms(
    request: SMSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Parse SMS and extract transaction data"""
    result = await transaction_controller.parse_sms(db, request.sms_text, user_id=current_user.id)
    transaction = result['transaction']
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.post("/parse-sms-local", response_model=TransactionResponse)
async def parse_sms_local(
    request: SMSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Parse SMS quickly using local regex-based parser (no LLM)"""
    result = transaction_controller.parse_sms_local_quick(db, request.sms_text, user_id=current_user.id)
    transaction = result['transaction']
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.post("/parse-sms-public", response_model=TransactionResponse)
async def parse_sms_public(request: SMSRequest, db: Session = Depends(get_db)):
    """Parse SMS without authentication (for backward compatibility)"""
    result = await transaction_controller.parse_sms(db, request.sms_text)
    transaction = result['transaction']
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.post("/parse-sms-local-public", response_model=TransactionResponse)
async def parse_sms_local_public(request: SMSRequest, db: Session = Depends(get_db)):
    """Parse SMS quickly using local regex-based parser without authentication"""
    result = transaction_controller.parse_sms_local_quick(db, request.sms_text, user_id=None)
    transaction = result['transaction']
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's transactions"""
    transactions = transaction_controller.get_transactions(db, current_user.id, limit, offset)
    
    return [
        TransactionResponse(
            id=t.id,
            vendor=t.vendor or "Unknown",
            amount=t.amount or 0.0,
            date=_date_to_str(t.date),
            category=t.category or "Others",
            sms_text=t.sms_text or "",
            confidence=t.confidence or 0.0
        )
        for t in transactions
    ]

@router.get("/transactions-public", response_model=List[TransactionResponse])
async def get_transactions_public(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all transactions (for backward compatibility)"""
    transactions = transaction_controller.get_transactions(db, None, limit, offset)
    
    return [
        TransactionResponse(
            id=t.id,
            vendor=t.vendor or "Unknown",
            amount=t.amount or 0.0,
            date=_date_to_str(t.date),
            category=t.category or "Others",
            sms_text=t.sms_text or "",
            confidence=t.confidence or 0.0
        )
        for t in transactions
    ]

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific transaction"""
    transaction = transaction_controller.get_transaction_by_id(db, transaction_id, current_user.id)
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new transaction manually"""
    transaction = transaction_controller.create_transaction(
        db=db,
        vendor=transaction_data.vendor,
        amount=transaction_data.amount,
        date=transaction_data.date,
        category=transaction_data.category,
        sms_text=transaction_data.sms_text,
        confidence=transaction_data.confidence,
        user_id=current_user.id
    )
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.post("/transactions-public", response_model=TransactionResponse)
async def create_transaction_public(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Create new transaction manually (backward compatibility)"""
    transaction = transaction_controller.create_transaction(
        db=db,
        vendor=transaction_data.vendor,
        amount=transaction_data.amount,
        date=transaction_data.date,
        category=transaction_data.category,
        sms_text=transaction_data.sms_text,
        confidence=transaction_data.confidence
    )
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update transaction"""
    transaction = transaction_controller.update_transaction(
        db, transaction_id, current_user.id, **transaction_data
    )
    
    return TransactionResponse(
        id=transaction.id,
        vendor=transaction.vendor,
        amount=transaction.amount,
        date=_date_to_str(transaction.date),
        category=transaction.category,
        sms_text=transaction.sms_text,
        confidence=transaction.confidence
    )

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete transaction"""
    return transaction_controller.delete_transaction(db, transaction_id, current_user.id)

@router.get("/search", response_model=List[TransactionResponse])
async def search_transactions(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search transactions"""
    transactions = transaction_controller.search_transactions(db, q, current_user.id, limit)
    
    return [
        TransactionResponse(
            id=t.id,
            vendor=t.vendor or "Unknown",
            amount=t.amount or 0.0,
            date=_date_to_str(t.date),
            category=t.category or "Others",
            sms_text=t.sms_text or "",
            confidence=t.confidence or 0.0
        )
        for t in transactions
    ]

@router.get("/ml-info")
async def get_ml_model_info():
    """Get ML model information"""
    return {
        "model_name": "llama3.1:latest",
        "model_type": "Ollama",
        "status": "active",
        "categories": [
            "Food Delivery",
            "E-commerce",
            "Transportation",
            "Entertainment",
            "Healthcare",
            "Utilities",
            "Education",
            "Shopping",
            "Travel",
            "Others"
        ],
        "capabilities": [
            "SMS transaction parsing",
            "Financial categorization",
            "Natural language processing",
            "Transaction analysis"
        ],
        "version": "1.0.0",
        "accuracy": "95%",
        "processing_time": "2-5 seconds"
    }
