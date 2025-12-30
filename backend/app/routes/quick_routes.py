"""Quick routes for Cloudflare compatibility"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.config.database import get_db, SessionLocal
from app.controllers.transaction_controller import TransactionController
from app.auth.dependencies import get_current_active_user
from app.models.user import User
import asyncio
import uuid
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/v1/quick", tags=["quick"])

# In-memory storage for async results
processing_results: Dict[str, Any] = {}

class SMSRequest(BaseModel):
    sms_text: str

# NEW: SMS message with metadata for fingerprint-based deduplication
class SMSMessageWithMetadata(BaseModel):
    sms_text: str
    sender: Optional[str] = None
    device_timestamp: Optional[int] = None

class SMSBatchRequest(BaseModel):
    # Legacy: list of SMS text strings
    sms_texts: Optional[List[str]] = None
    # NEW: list of SMS messages with metadata (sender, timestamp)
    sms_messages: Optional[List[SMSMessageWithMetadata]] = None
    batch_size: Optional[int] = 10
    delay_seconds: Optional[int] = 3

class QuickResponse(BaseModel):
    job_id: str
    status: str
    message: str

class QuickBatchResponse(BaseModel):
    job_id: str
    status: str
    message: str
    total: int

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

transaction_controller = TransactionController()

async def process_sms_async(job_id: str, sms_text: str, user_id: Optional[int]):
    db_session = SessionLocal()
    try:
        result = await transaction_controller.parse_sms(db_session, sms_text, user_id=user_id)
        processing_results[job_id] = {
            "status": "completed",
            "result": {
                "success": True,
                "transaction": {
                    "id": result['transaction'].id,
                    "vendor": result['transaction'].vendor,
                    "amount": result['transaction'].amount,
                    "category": result['transaction'].category,
                    "confidence": result['transaction'].confidence
                }
            }
        }
    except Exception as e:
        processing_results[job_id] = {
            "status": "failed",
            "error": str(e)
        }
    finally:
        db_session.close()

async def process_sms_local_async(job_id: str, sms_text: str, user_id: Optional[int]):
    db_session = SessionLocal()
    try:
        result = transaction_controller.parse_sms_local_quick(db_session, sms_text, user_id=user_id)
        processing_results[job_id] = {
            "status": "completed",
            "result": {
                "success": True,
                "transaction": {
                    "id": result['transaction'].id,
                    "vendor": result['transaction'].vendor,
                    "amount": result['transaction'].amount,
                    "category": result['transaction'].category,
                    "confidence": result['transaction'].confidence
                }
            }
        }
    except Exception as e:
        processing_results[job_id] = {
            "status": "failed",
            "error": str(e)
        }
    finally:
        db_session.close()

@router.post("/parse-sms", response_model=QuickResponse)
async def quick_parse_sms(
    request: SMSRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(process_sms_async, job_id, request.sms_text, current_user.id)
    processing_results[job_id] = {"status": "processing"}
    return QuickResponse(job_id=job_id, status="processing", message="SMS parsing started. Check status with job_id.")

@router.post("/parse-sms-local", response_model=QuickResponse)
async def quick_parse_sms_local(
    request: SMSRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(process_sms_local_async, job_id, request.sms_text, current_user.id)
    processing_results[job_id] = {"status": "processing"}
    return QuickResponse(job_id=job_id, status="processing", message="Local SMS parsing started. Check status with job_id.")

async def process_sms_batch_async(job_id: str, sms_items: List[Dict[str, Any]], user_id: int, batch_size: int, delay_seconds: int):
    """Process SMS batch with optional metadata for fingerprint deduplication"""
    processing_results[job_id] = {"status": "running", "total": len(sms_items), "processed": 0, "success": 0, "failed": 0, "items": []}
    processed = 0
    success = 0
    failed = 0
    items: List[Dict[str, Any]] = []

    # Helper: process a single SMS with its own DB session
    async def _process_one(sms_item: Dict[str, Any]) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            # Extract metadata if available
            sms_text = sms_item.get('sms_text') or sms_item.get('text') or str(sms_item)
            sender = sms_item.get('sender')
            device_timestamp = sms_item.get('device_timestamp')
            
            # Pass metadata to controller for fingerprint dedup
            result = await transaction_controller.parse_sms(
                db, 
                sms_text, 
                user_id=user_id,
                sender=sender,
                device_timestamp=device_timestamp
            )
            t = result['transaction']
            return {
                "ok": True,
                "transaction_id": t.id,
                "vendor": t.vendor,
                "amount": t.amount,
                "category": t.category,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            db.close()

    try:
        n = len(sms_items)
        i = 0
        while i < n:
            chunk = sms_items[i:i + max(1, batch_size)]
            # Process this chunk concurrently
            results = await asyncio.gather(*[_process_one(item) for item in chunk], return_exceptions=False)

            for r in results:
                if r.get("ok"):
                    success += 1
                    items.append({
                        "success": True,
                        "transaction_id": r.get("transaction_id"),
                        "vendor": r.get("vendor"),
                        "amount": r.get("amount"),
                        "category": r.get("category"),
                    })
                else:
                    failed += 1
                    items.append({"success": False, "error": r.get("error")})
                processed += 1

            processing_results[job_id] = {
                "status": "running",
                "total": n,
                "processed": processed,
                "success": success,
                "failed": failed,
                "items": items[-10:]
            }

            i += len(chunk)
            if delay_seconds and i < n:
                await asyncio.sleep(max(0, delay_seconds))

        processing_results[job_id] = {
            "status": "completed",
            "total": n,
            "processed": processed,
            "success": success,
            "failed": failed,
            "items": items
        }
    except Exception as e:
        processing_results[job_id] = {"status": "failed", "error": str(e), "processed": processed, "success": success, "failed": failed}

async def process_sms_batch_local_async(job_id: str, sms_items: List[Dict[str, Any]], user_id: int, batch_size: int, delay_seconds: int):
    """Process SMS batch locally with optional metadata for fingerprint deduplication"""
    processing_results[job_id] = {"status": "running", "total": len(sms_items), "processed": 0, "success": 0, "failed": 0, "items": []}
    processed = 0
    success = 0
    failed = 0
    items: List[Dict[str, Any]] = []

    def _process_one_sync(sms_item: Dict[str, Any]) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            # Extract metadata if available
            sms_text = sms_item.get('sms_text') or sms_item.get('text') or str(sms_item)
            sender = sms_item.get('sender')
            device_timestamp = sms_item.get('device_timestamp')
            
            # Pass metadata to controller for fingerprint dedup
            result = transaction_controller.parse_sms_local_quick(
                db, 
                sms_text, 
                user_id=user_id,
                sender=sender,
                device_timestamp=device_timestamp
            )
            t = result['transaction']
            return {
                "ok": True,
                "transaction_id": t.id,
                "vendor": t.vendor,
                "amount": t.amount,
                "category": t.category,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            db.close()

    try:
        n = len(sms_items)
        i = 0
        while i < n:
            chunk = sms_items[i:i + max(1, batch_size)]
            # OPTIMIZED: Process entire chunk in parallel using gather
            loop = asyncio.get_running_loop()
            tasks = [loop.run_in_executor(None, _process_one_sync, item) for item in chunk]
            results = await asyncio.gather(*tasks)

            for r in results:
                if r.get("ok"):
                    success += 1
                    items.append({
                        "success": True,
                        "transaction_id": r.get("transaction_id"),
                        "vendor": r.get("vendor"),
                        "amount": r.get("amount"),
                        "category": r.get("category"),
                    })
                else:
                    failed += 1
                    items.append({"success": False, "error": r.get("error")})
                processed += 1

            processing_results[job_id] = {
                "status": "running",
                "total": n,
                "processed": processed,
                "success": success,
                "failed": failed,
                "items": items[-10:]
            }

            i += len(chunk)
            if delay_seconds and i < n:
                await asyncio.sleep(max(0, delay_seconds))

        processing_results[job_id] = {
            "status": "completed",
            "total": n,
            "processed": processed,
            "success": success,
            "failed": failed,
            "items": items
        }
    except Exception as e:
        processing_results[job_id] = {"status": "failed", "error": str(e), "processed": processed, "success": success, "failed": failed}

@router.post("/parse-sms-batch", response_model=QuickBatchResponse)
async def quick_parse_sms_batch(
    request: SMSBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    # Convert to unified format - support both sms_texts (legacy) and sms_messages (new)
    if request.sms_messages:
        # NEW: sms_messages with metadata
        sms_items = [{"sms_text": m.sms_text, "sender": m.sender, "device_timestamp": m.device_timestamp} for m in request.sms_messages]
    elif request.sms_texts:
        # LEGACY: plain text strings
        sms_items = [{"sms_text": txt} for txt in request.sms_texts]
    else:
        sms_items = []
    
    job_id = str(uuid.uuid4())
    processing_results[job_id] = {"status": "queued", "total": len(sms_items), "processed": 0, "success": 0, "failed": 0}
    
    safe_batch = request.batch_size or 5
    if safe_batch < 1:
        safe_batch = 1
    if safe_batch > 10:
        safe_batch = 10
        
    background_tasks.add_task(
        process_sms_batch_async,
        job_id,
        sms_items,  # Now passing dict items with metadata
        current_user.id,
        safe_batch,
        request.delay_seconds if request.delay_seconds is not None else 2
    )
    return QuickBatchResponse(job_id=job_id, status="queued", message="Batch parsing started. Poll job status.", total=len(sms_items))

@router.post("/parse-sms-batch-local", response_model=QuickBatchResponse)
async def quick_parse_sms_batch_local(
    request: SMSBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    import time
    start_time = time.time()
    
    # Convert to unified format - support both sms_texts (legacy) and sms_messages (new)
    if request.sms_messages:
        # NEW: sms_messages with metadata for fingerprint dedup
        sms_items = [{"sms_text": m.sms_text, "sender": m.sender, "device_timestamp": m.device_timestamp} for m in request.sms_messages]
        print(f"🔧 [BATCH-LOCAL] Using NEW metadata format: {len(sms_items)} SMS with sender/timestamp")
    elif request.sms_texts:
        # LEGACY: plain text strings
        sms_items = [{"sms_text": txt} for txt in request.sms_texts]
        print(f"🔧 [BATCH-LOCAL] Using LEGACY format: {len(sms_items)} SMS (text only)")
    else:
        sms_items = []
    
    print(f"🔧 [BATCH-LOCAL] Request received: {len(sms_items)} SMS, batch_size={request.batch_size}")
    
    job_id = str(uuid.uuid4())
    processing_results[job_id] = {"status": "queued", "total": len(sms_items), "processed": 0, "success": 0, "failed": 0}
    
    safe_batch = request.batch_size or 20
    if safe_batch < 1:
        safe_batch = 1
    if safe_batch > 50:
        safe_batch = 50
    
    print(f"🔧 [BATCH-LOCAL] Starting background task with batch_size={safe_batch}, job_id={job_id}")
    background_tasks.add_task(
        process_sms_batch_local_async,
        job_id,
        sms_items,  # Now passing dict items with metadata
        current_user.id,
        safe_batch,
        request.delay_seconds if request.delay_seconds is not None else 0
    )
    
    elapsed = time.time() - start_time
    print(f"✅ [BATCH-LOCAL] Responding with job_id={job_id} (took {elapsed:.2f}s)")
    return QuickBatchResponse(job_id=job_id, status="queued", message="Local batch parsing started. Poll job status.", total=len(sms_items))

@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    if job_id not in processing_results:
        return JobStatusResponse(job_id=job_id, status="not_found", error="Job ID not found")
    job_data = processing_results[job_id]
    resp = {
        "job_id": job_id,
        "status": job_data.get("status", "unknown"),
        # Always expose progress info under 'result' for a consistent shape
        "result": job_data
    }
    if job_data.get("error") is not None:
        resp["error"] = job_data.get("error")
    return JobStatusResponse(**resp)

@router.delete("/job/{job_id}")
async def cleanup_job(job_id: str):
    if job_id in processing_results:
        del processing_results[job_id]
        return {"message": "Job cleaned up"}
    return {"message": "Job not found"}
