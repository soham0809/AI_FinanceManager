"""Routes for intelligent SMS filtering and analysis"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from app.config.database import get_db
from app.utils.intelligent_sms_filter import IntelligentSMSFilter, SMSType
from app.auth.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/v1/intelligent-filter", tags=["intelligent-filter"])

class SMSAnalysisRequest(BaseModel):
    sms_texts: List[str]

class SMSFilterRequest(BaseModel):
    sms_text: str
    sender: str = ""

class FilteredSMSResponse(BaseModel):
    original_count: int
    filtered_count: int
    real_transactions: List[str]
    filtered_out: Dict[str, List[str]]
    analysis: Dict[str, Any]

@router.post("/analyze-sms-batch", response_model=Dict[str, Any])
async def analyze_sms_batch(
    request: SMSAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a batch of SMS messages for intelligent filtering"""
    filter_system = IntelligentSMSFilter()
    
    # Convert to format expected by filter
    sms_list = [{"text": sms, "sender": ""} for sms in request.sms_texts]
    
    # Analyze the batch
    analysis = filter_system.analyze_sms_batch(sms_list)
    
    return {
        "user_id": current_user.id,
        "analysis": analysis,
        "summary": {
            "total_sms": analysis["total"],
            "real_transactions": analysis["real_transactions"],
            "promotional": analysis["promotional"],
            "notifications": analysis["notifications"],
            "spam": analysis["spam"],
            "unknown": analysis["unknown"],
            "quality_score": round((analysis["real_transactions"] / analysis["total"]) * 100, 1) if analysis["total"] > 0 else 0
        }
    }

@router.post("/filter-real-transactions", response_model=FilteredSMSResponse)
async def filter_real_transactions(
    request: SMSAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Filter SMS messages to return only real financial transactions"""
    filter_system = IntelligentSMSFilter()
    
    # Convert to format expected by filter
    sms_list = [{"text": sms, "sender": ""} for sms in request.sms_texts]
    
    # Filter for real transactions
    real_transactions = filter_system.filter_real_transactions(sms_list)
    
    # Analyze all messages for detailed breakdown
    analysis = filter_system.analyze_sms_batch(sms_list)
    
    # Categorize filtered out messages
    filtered_out = {
        "promotional": [],
        "notifications": [],
        "spam": [],
        "unknown": []
    }
    
    for detail in analysis["details"]:
        if detail["type"] != "real_transaction":
            filtered_out[detail["type"]].append(detail["text"])
    
    return FilteredSMSResponse(
        original_count=len(request.sms_texts),
        filtered_count=len(real_transactions),
        real_transactions=[tx["text"] for tx in real_transactions],
        filtered_out=filtered_out,
        analysis=analysis
    )

@router.post("/classify-single-sms")
async def classify_single_sms(
    request: SMSFilterRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Classify a single SMS message"""
    filter_system = IntelligentSMSFilter()
    
    sms_type, confidence, reason = filter_system.classify_sms(request.sms_text, request.sender)
    
    return {
        "sms_text": request.sms_text[:100] + "..." if len(request.sms_text) > 100 else request.sms_text,
        "sender": request.sender,
        "classification": {
            "type": sms_type.value,
            "confidence": round(confidence, 3),
            "reason": reason
        },
        "is_real_transaction": sms_type == SMSType.REAL_TRANSACTION and confidence > 0.6,
        "should_process": sms_type == SMSType.REAL_TRANSACTION and confidence > 0.6
    }

@router.get("/quality-report")
async def get_quality_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get quality report of existing transactions in database"""
    from app.controllers.transaction_controller import TransactionController
    
    controller = TransactionController()
    
    # Get all user transactions
    transactions = controller.get_transactions(db, current_user.id, limit=200)
    
    if not transactions:
        return {"message": "No transactions found"}
    
    # Analyze existing transactions
    sms_list = [{"text": tx.sms_text, "sender": ""} for tx in transactions if tx.sms_text]
    
    if not sms_list:
        return {"message": "No SMS text found in transactions"}
    
    analysis = controller.intelligent_filter.analyze_sms_batch(sms_list)
    
    return {
        "total_transactions_in_db": len(transactions),
        "transactions_with_sms_text": len(sms_list),
        "quality_analysis": analysis,
        "recommendations": {
            "real_transactions": analysis["real_transactions"],
            "should_remove_promotional": analysis["promotional"],
            "should_remove_notifications": analysis["notifications"],
            "should_remove_spam": analysis["spam"],
            "quality_improvement": f"Remove {analysis['promotional'] + analysis['notifications'] + analysis['spam']} non-financial entries to improve quality"
        }
    }
