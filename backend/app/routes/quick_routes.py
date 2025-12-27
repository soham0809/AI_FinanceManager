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

class SMSBatchRequest(BaseModel):
    sms_texts: List[str]
    batch_size: Optional[int] = 3
    delay_seconds: Optional[int] = 8

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

async def process_sms_batch_async(job_id: str, sms_texts: List[str], user_id: int, batch_size: int, delay_seconds: int):
    processing_results[job_id] = {"status": "running", "total": len(sms_texts), "processed": 0, "success": 0, "failed": 0, "items": []}
    processed = 0
    success = 0
    failed = 0
    items: List[Dict[str, Any]] = []

    # Helper: process a single SMS with its own DB session
    async def _process_one(sms_text: str) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            result = await transaction_controller.parse_sms(db, sms_text, user_id=user_id)
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
        n = len(sms_texts)
        i = 0
        while i < n:
            chunk = sms_texts[i:i + max(1, batch_size)]
            # Process this chunk concurrently
            results = await asyncio.gather(*[ _process_one(txt) for txt in chunk ], return_exceptions=False)

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

async def process_sms_batch_local_async(job_id: str, sms_texts: List[str], user_id: int, batch_size: int, delay_seconds: int):
    processing_results[job_id] = {"status": "running", "total": len(sms_texts), "processed": 0, "success": 0, "failed": 0, "items": []}
    processed = 0
    success = 0
    failed = 0
    items: List[Dict[str, Any]] = []

    def _process_one_sync(sms_text: str) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            result = transaction_controller.parse_sms_local_quick(db, sms_text, user_id=user_id)
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
        n = len(sms_texts)
        i = 0
        while i < n:
            chunk = sms_texts[i:i + max(1, batch_size)]
            # Process this chunk concurrently using thread pool executor (Python 3.8 compatible)
            results: List[Dict[str, Any]] = []
            loop = asyncio.get_running_loop()
            for txt in chunk:
                r = await loop.run_in_executor(None, _process_one_sync, txt)
                results.append(r)

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
    job_id = str(uuid.uuid4())
    processing_results[job_id] = {"status": "queued", "total": len(request.sms_texts), "processed": 0, "success": 0, "failed": 0}
    # Sanitize batch size to 1..5 (ultra-conservative for 100 SMS)
    safe_batch = request.batch_size or 3
    if safe_batch < 1:
        safe_batch = 1
    if safe_batch > 5:
        safe_batch = 5
    background_tasks.add_task(
        process_sms_batch_async,
        job_id,
        request.sms_texts,
        current_user.id,
        safe_batch,
        request.delay_seconds or 8
    )
    return QuickBatchResponse(job_id=job_id, status="queued", message="Batch parsing started. Poll job status.", total=len(request.sms_texts))

@router.post("/parse-sms-batch-local", response_model=QuickBatchResponse)
async def quick_parse_sms_batch_local(
    request: SMSBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    import time
    start_time = time.time()
    print(f"🔧 [BATCH-LOCAL] Request received: {len(request.sms_texts)} SMS, batch_size={request.batch_size}")
    
    job_id = str(uuid.uuid4())
    processing_results[job_id] = {"status": "queued", "total": len(request.sms_texts), "processed": 0, "success": 0, "failed": 0}
    safe_batch = request.batch_size or 5
    if safe_batch < 1:
        safe_batch = 1
    if safe_batch > 20:
        safe_batch = 20
    
    print(f"🔧 [BATCH-LOCAL] Starting background task with batch_size={safe_batch}, job_id={job_id}")
    background_tasks.add_task(
        process_sms_batch_local_async,
        job_id,
        request.sms_texts,
        current_user.id,
        safe_batch,
        request.delay_seconds or 1
    )
    
    elapsed = time.time() - start_time
    print(f"✅ [BATCH-LOCAL] Responding with job_id={job_id} (took {elapsed:.2f}s)")
    return QuickBatchResponse(job_id=job_id, status="queued", message="Local batch parsing started. Poll job status.", total=len(request.sms_texts))

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
