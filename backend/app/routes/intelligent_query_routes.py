"""Intelligent Query Cache Routes - Fast financial Q&A using parsed transactions"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.utils.intelligent_query_cache import IntelligentQueryCache

router = APIRouter(prefix="/v1/intelligent-query", tags=["intelligent-query"])

# Global cache instance
query_cache = IntelligentQueryCache()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    response: str
    cached: bool
    processing_time: float
    timestamp: str

@router.post("/ask", response_model=QueryResponse)
async def ask_financial_question(
    request: QueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ask any financial question about your transactions"""
    
    try:
        result = await query_cache.get_cached_response(
            request.query, 
            current_user.id, 
            db
        )
        
        return QueryResponse(
            success=True,
            response=result["response"],
            cached=result["cached"],
            processing_time=result["processing_time"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/pre-cache")
async def pre_cache_common_queries(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Pre-cache common financial queries for faster access"""
    
    # Start pre-caching in background
    background_tasks.add_task(
        _background_pre_cache,
        current_user.id,
        db
    )
    
    return {
        "success": True,
        "message": "Pre-caching common queries started in background",
        "user_id": current_user.id,
        "queries_to_cache": len(query_cache.common_queries)
    }

async def _background_pre_cache(user_id: int, db: Session):
    """Background task for pre-caching"""
    try:
        result = await query_cache.pre_cache_common_queries(user_id, db)
        print(f"Pre-caching completed for user {user_id}: {result}")
    except Exception as e:
        print(f"Pre-caching failed for user {user_id}: {str(e)}")

@router.get("/cache-stats")
async def get_cache_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get cache statistics for current user"""
    
    try:
        stats = query_cache.get_cache_stats(current_user.id)
        
        return {
            "success": True,
            "user_id": current_user.id,
            "cache_stats": stats,
            "message": f"Cache contains {stats['valid_cached_queries']} valid queries"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@router.get("/common-queries")
async def get_common_queries():
    """Get list of common pre-cacheable queries"""
    
    return {
        "success": True,
        "common_queries": query_cache.common_queries,
        "total_queries": len(query_cache.common_queries),
        "description": "These queries are automatically pre-cached for faster access"
    }

@router.post("/clear-cache")
async def clear_user_cache(
    current_user: User = Depends(get_current_active_user)
):
    """Clear cache for current user"""
    
    try:
        cleared_count = query_cache.clear_user_cache(current_user.id)
        
        return {
            "success": True,
            "message": f"Cleared {cleared_count} cached queries",
            "user_id": current_user.id,
            "cleared_queries": cleared_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.get("/quick-insights")
async def get_quick_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get quick financial insights using cached queries"""
    
    try:
        insights = []
        
        # Get pre-cached common queries
        for query in query_cache.common_queries[:3]:  # Top 3 insights
            result = await query_cache.get_cached_response(query, current_user.id, db)
            insights.append({
                "question": query,
                "answer": result["response"],
                "cached": result["cached"]
            })
        
        return {
            "success": True,
            "insights": insights,
            "user_id": current_user.id,
            "message": "Quick financial insights based on your transaction data"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@router.post("/batch-query")
async def batch_query_processing(
    queries: list[str],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process multiple queries in batch"""
    
    if len(queries) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 queries allowed per batch")
    
    try:
        results = []
        
        for query in queries:
            result = await query_cache.get_cached_response(query, current_user.id, db)
            results.append({
                "query": query,
                "response": result["response"],
                "cached": result["cached"],
                "processing_time": result["processing_time"]
            })
        
        total_time = sum(r["processing_time"] for r in results)
        cached_count = sum(1 for r in results if r["cached"])
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "total_queries": len(queries),
                "cached_responses": cached_count,
                "new_responses": len(queries) - cached_count,
                "total_processing_time": total_time
            },
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch queries: {str(e)}")
