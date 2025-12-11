"""Spending Analytics Routes - Monthly and Weekly spending analysis"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.utils.spending_analytics import SpendingAnalytics

router = APIRouter(prefix="/v1/spending", tags=["spending-analytics"])

@router.get("/monthly")
async def get_monthly_spending(
    months: int = Query(6, description="Number of months to analyze", ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get monthly spending breakdown"""
    analytics = SpendingAnalytics()
    
    try:
        result = analytics.get_monthly_spending(db, current_user.id, months)
        
        if "error" in result:
            return {
                "success": False,
                "message": result["error"],
                "data": None
            }
        
        return {
            "success": True,
            "message": f"Monthly spending data for last {months} months",
            "data": result,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing monthly spending: {str(e)}")

@router.get("/weekly")
async def get_weekly_spending(
    weeks: int = Query(8, description="Number of weeks to analyze", ge=1, le=16),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get weekly spending breakdown"""
    analytics = SpendingAnalytics()
    
    try:
        result = analytics.get_weekly_spending(db, current_user.id, weeks)
        
        if "error" in result:
            return {
                "success": False,
                "message": result["error"],
                "data": None
            }
        
        return {
            "success": True,
            "message": f"Weekly spending data for last {weeks} weeks",
            "data": result,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing weekly spending: {str(e)}")

@router.get("/trends")
async def get_spending_trends(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get spending trends and insights"""
    analytics = SpendingAnalytics()
    
    try:
        result = analytics.get_spending_trends(db, current_user.id)
        
        if "error" in result:
            return {
                "success": False,
                "message": result["error"],
                "data": None
            }
        
        return {
            "success": True,
            "message": "Spending trends analysis",
            "data": result,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing spending trends: {str(e)}")

@router.get("/summary")
async def get_spending_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive spending summary"""
    analytics = SpendingAnalytics()
    
    try:
        # Get both monthly and weekly data
        monthly_result = analytics.get_monthly_spending(db, current_user.id, 3)
        weekly_result = analytics.get_weekly_spending(db, current_user.id, 4)
        trends_result = analytics.get_spending_trends(db, current_user.id)
        
        # Calculate total spending
        total_spending = 0
        total_transactions = 0
        
        if "monthly_spending" in monthly_result:
            for month in monthly_result["monthly_spending"]:
                total_spending += month["total_spent"]
                total_transactions += month["transaction_count"]
        
        # Get top categories across all time
        all_categories = {}
        if "monthly_spending" in monthly_result:
            for month in monthly_result["monthly_spending"]:
                for category, amount in month["categories"].items():
                    all_categories[category] = all_categories.get(category, 0) + amount
        
        top_categories = dict(sorted(all_categories.items(), key=lambda x: x[1], reverse=True)[:5])
        
        summary = {
            "total_spending": round(total_spending, 2),
            "total_transactions": total_transactions,
            "average_transaction": round(total_spending / total_transactions, 2) if total_transactions > 0 else 0,
            "top_categories": top_categories,
            "recent_monthly": monthly_result.get("monthly_spending", [])[:3],
            "recent_weekly": weekly_result.get("weekly_spending", [])[:2],
            "trends": trends_result if "error" not in trends_result else None
        }
        
        return {
            "success": True,
            "message": "Comprehensive spending summary",
            "data": summary,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating spending summary: {str(e)}")

@router.get("/category/{category_name}")
async def get_category_spending(
    category_name: str,
    months: int = Query(6, description="Number of months to analyze", ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown for a specific category"""
    analytics = SpendingAnalytics()
    
    try:
        # Get monthly data and filter by category
        monthly_result = analytics.get_monthly_spending(db, current_user.id, months)
        
        if "error" in monthly_result:
            return {
                "success": False,
                "message": monthly_result["error"],
                "data": None
            }
        
        category_data = []
        total_category_spending = 0
        
        for month in monthly_result["monthly_spending"]:
            category_amount = month["categories"].get(category_name, 0)
            if category_amount > 0:
                category_data.append({
                    "month": month["month_name"],
                    "amount": category_amount,
                    "percentage_of_month": round((category_amount / month["total_spent"]) * 100, 1) if month["total_spent"] > 0 else 0
                })
                total_category_spending += category_amount
        
        return {
            "success": True,
            "message": f"Spending analysis for category: {category_name}",
            "data": {
                "category": category_name,
                "total_spending": round(total_category_spending, 2),
                "monthly_breakdown": category_data,
                "average_monthly": round(total_category_spending / len(category_data), 2) if category_data else 0
            },
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing category spending: {str(e)}")
