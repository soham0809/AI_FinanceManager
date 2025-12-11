"""Batch processing routes for transaction re-processing"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.config.database import get_db
from app.utils.batch_processor import BatchTransactionProcessor

router = APIRouter(prefix="/v1/batch", tags=["batch-processing"])

class BatchProcessingRequest(BaseModel):
    limit: Optional[int] = None
    batch_size: Optional[int] = 3
    delay_between_batches: Optional[int] = 5

class BatchProcessingResponse(BaseModel):
    success: bool
    message: str
    job_id: Optional[str] = None

# Store for background job status
batch_jobs = {}

@router.post("/process-transactions", response_model=BatchProcessingResponse)
async def start_batch_processing(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start batch processing of transactions in the background"""
    try:
        import uuid
        job_id = str(uuid.uuid4())
        
        # Initialize batch processor with custom settings
        processor = BatchTransactionProcessor(
            batch_size=request.batch_size,
            delay_between_batches=request.delay_between_batches
        )
        
        # Add background task
        background_tasks.add_task(
            run_batch_processing_job,
            job_id,
            processor,
            db,
            request.limit
        )
        
        # Store job info
        batch_jobs[job_id] = {
            'status': 'started',
            'started_at': None,
            'completed_at': None,
            'result': None
        }
        
        return BatchProcessingResponse(
            success=True,
            message=f"Batch processing job started with ID: {job_id}",
            job_id=job_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a batch processing job"""
    if job_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return batch_jobs[job_id]

@router.get("/preview")
async def preview_transactions_for_processing(
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """Preview transactions that would be processed"""
    try:
        processor = BatchTransactionProcessor()
        transactions = processor.get_transactions_for_processing(db, limit=limit)
        
        preview_data = []
        for transaction in transactions:
            # Handle date formatting properly
            date_str = transaction.date.isoformat() if isinstance(transaction.date, datetime) else str(transaction.date)
            
            preview_data.append({
                'id': transaction.id,
                'vendor': transaction.vendor,
                'amount': transaction.amount,
                'date': date_str,
                'category': transaction.category,
                'confidence': transaction.confidence,
                'sms_text': transaction.sms_text[:100] + "..." if transaction.sms_text and len(transaction.sms_text) > 100 else transaction.sms_text
            })
        
        return {
            'success': True,
            'total_available': len(transactions),
            'preview': preview_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview transactions: {str(e)}")

async def run_batch_processing_job(job_id: str, processor: BatchTransactionProcessor, db: Session, limit: Optional[int]):
    """Background job for batch processing"""
    from datetime import datetime
    
    try:
        batch_jobs[job_id]['status'] = 'running'
        batch_jobs[job_id]['started_at'] = datetime.now().isoformat()
        
        # Run batch processing
        result = processor.process_all_transactions(db, limit=limit)
        
        batch_jobs[job_id]['status'] = 'completed'
        batch_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        batch_jobs[job_id]['result'] = result
        
    except Exception as e:
        batch_jobs[job_id]['status'] = 'failed'
        batch_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        batch_jobs[job_id]['error'] = str(e)
