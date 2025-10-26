"""Enhanced transaction routes with intelligent filtering"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.controllers.transaction_controller import TransactionController
from app.utils.intelligent_sms_filter import IntelligentSMSFilter, SMSType
import uuid

router = APIRouter(prefix="/v1/enhanced", tags=["enhanced-transactions"])

class IntelligentSMSBatchRequest(BaseModel):
    sms_texts: List[str]
    filter_promotional: bool = True
    confidence_threshold: float = 0.6

class EnhancedTransactionResponse(BaseModel):
    job_id: str
    status: str
    message: str
    filtering_stats: Dict[str, int]

# In-memory storage for processing results
processing_results: Dict[str, Any] = {}

@router.post("/intelligent-sms-processing", response_model=EnhancedTransactionResponse)
async def intelligent_sms_processing(
    request: IntelligentSMSBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process SMS messages with intelligent filtering - only real transactions"""
    
    job_id = str(uuid.uuid4())
    
    # Initialize intelligent filter
    filter_system = IntelligentSMSFilter()
    
    # Pre-filter SMS messages
    if request.filter_promotional:
        # Convert to filter format
        sms_list = [{"text": sms, "sender": ""} for sms in request.sms_texts]
        
        # Analyze batch
        analysis = filter_system.analyze_sms_batch(sms_list)
        
        # Filter for real transactions only
        real_transactions = filter_system.filter_real_transactions(sms_list)
        filtered_sms_texts = [tx["text"] for tx in real_transactions]
        
        filtering_stats = {
            "original_count": len(request.sms_texts),
            "real_transactions": analysis["real_transactions"],
            "promotional_filtered": analysis["promotional"],
            "notifications_filtered": analysis["notifications"],
            "spam_filtered": analysis["spam"],
            "final_count": len(filtered_sms_texts)
        }
    else:
        filtered_sms_texts = request.sms_texts
        filtering_stats = {
            "original_count": len(request.sms_texts),
            "final_count": len(request.sms_texts),
            "filtering_disabled": True
        }
    
    # Initialize processing results
    processing_results[job_id] = {
        "status": "processing",
        "total": len(filtered_sms_texts),
        "processed": 0,
        "success": 0,
        "failed": 0,
        "filtering_stats": filtering_stats,
        "transactions": []
    }
    
    # Start background processing
    background_tasks.add_task(
        process_intelligent_sms_batch,
        job_id,
        filtered_sms_texts,
        current_user.id,
        request.confidence_threshold
    )
    
    return EnhancedTransactionResponse(
        job_id=job_id,
        status="processing",
        message=f"Intelligent processing started. Filtered {filtering_stats['original_count']} SMS to {filtering_stats['final_count']} real transactions.",
        filtering_stats=filtering_stats
    )

async def process_intelligent_sms_batch(
    job_id: str,
    sms_texts: List[str],
    user_id: int,
    confidence_threshold: float
):
    """Background task to process filtered SMS messages"""
    from app.config.database import SessionLocal
    
    db = SessionLocal()
    controller = TransactionController()
    
    try:
        processed = 0
        success = 0
        failed = 0
        transactions = []
        
        for sms_text in sms_texts:
            try:
                # Process with intelligent filtering already applied
                result = await controller.parse_sms(db, sms_text, user_id)
                
                if result.get('success', False):
                    success += 1
                    # Access Transaction object fields correctly
                    transaction = result.get('transaction')
                    transactions.append({
                        "vendor": transaction.vendor,
                        "amount": transaction.amount,
                        "category": transaction.category,
                        "confidence": transaction.confidence
                    })
                else:
                    failed += 1
                    
            except Exception as e:
                failed += 1
                print(f"Failed to process SMS: {str(e)}")
            
            processed += 1
            
            # Update progress
            processing_results[job_id].update({
                "processed": processed,
                "success": success,
                "failed": failed,
                "transactions": transactions
            })
        
        # Mark as complete
        processing_results[job_id]["status"] = "completed"
        
    except Exception as e:
        processing_results[job_id]["status"] = "failed"
        processing_results[job_id]["error"] = str(e)
        
    finally:
        db.close()

@router.get("/job-status/{job_id}")
async def get_enhanced_job_status(job_id: str):
    """Get status of intelligent SMS processing job"""
    if job_id not in processing_results:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return processing_results[job_id]

@router.get("/quality-dashboard")
async def get_quality_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quality dashboard showing intelligent filtering results"""
    controller = TransactionController()
    
    # Get user transactions
    transactions = controller.get_transactions(db, current_user.id, limit=100)
    
    if not transactions:
        return {
            "message": "No transactions found",
            "quality_score": 0,
            "recommendations": ["Start by processing some SMS messages"]
        }
    
    # Analyze quality
    sms_list = [{"text": tx.sms_text, "sender": ""} for tx in transactions if tx.sms_text]
    
    if not sms_list:
        return {
            "message": "No SMS data found",
            "quality_score": 0
        }
    
    analysis = controller.intelligent_filter.analyze_sms_batch(sms_list)
    
    quality_score = (analysis["real_transactions"] / analysis["total"]) * 100 if analysis["total"] > 0 else 0
    
    recommendations = []
    if quality_score < 50:
        recommendations.append("Enable intelligent filtering to improve data quality")
    if analysis["promotional"] > 0:
        recommendations.append(f"Remove {analysis['promotional']} promotional messages")
    if analysis["notifications"] > 0:
        recommendations.append(f"Remove {analysis['notifications']} notification messages")
    
    return {
        "total_transactions": len(transactions),
        "quality_analysis": analysis,
        "quality_score": round(quality_score, 1),
        "recommendations": recommendations,
        "intelligent_filtering_available": True
    }
