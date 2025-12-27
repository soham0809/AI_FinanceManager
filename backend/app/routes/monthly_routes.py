"""Monthly Analytics Routes - Added for mobile app compatibility"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.utils.spending_analytics import SpendingAnalytics
from datetime import datetime

router = APIRouter(prefix="/v1/analytics", tags=["monthly-analytics"])


@router.get("/monthly/summary")
async def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    year: Optional[int] = Query(None, description="Year to get summary for"),
    month: Optional[int] = Query(None, description="Month to get summary for (1-12)")
):
    """
    Get monthly summary of transactions for a specific month.
    If year/month not provided, defaults to current month.
    """
    try:
        analytics = SpendingAnalytics()
        
        # Get current date if not specified
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        
        # Get monthly spending data
        monthly_data = analytics.get_monthly_spending(db, current_user.id, months=12)
        
        if "error" in monthly_data:
            return {
                "success": False,
                "message": monthly_data["error"],
                "data": None
            }
        
        # Find the specific month
        target_month = f"{year}-{month:02d}"
        month_summary = None
        
        for month_data in monthly_data.get("monthly_spending", []):
            if month_data["month"] == target_month:
                month_summary = month_data
                break
        
        if not month_summary:
            return {
                "success": False,
                "message": f"No data found for {year}-{month:02d}",
                "data": {
                    "month": target_month,
                    "total_spent": 0,
                    "transaction_count": 0,
                    "categories": {},
                    "top_vendors": {}
                }
            }
        
        return {
            "success": True,
            "message": f"Monthly summary for {month_summary['month_name']}",
            "data": month_summary,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monthly summary: {str(e)}")


@router.get("/monthly/yearly-overview")
async def get_yearly_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    year: Optional[int] = Query(None, description="Year to get overview for")
):
    """
    Get yearly overview of all months.
    If year not provided, defaults to current year.
    """
    try:
        analytics = SpendingAnalytics()
        
        # Get current year if not specified
        year = year or datetime.now().year
        
        # Get all monthly data for the year
        all_monthly_data = analytics.get_monthly_spending(db, current_user.id, months=12)
        
        if "error" in all_monthly_data:
            return {
                "success": False,
                "message": all_monthly_data["error"],
                "data": None
            }
        
        # Filter for the specified year
        yearly_months = []
        total_year_spending = 0
        total_year_transactions = 0
        all_categories = {}
        
        for month_data in all_monthly_data.get("monthly_spending", []):
            if month_data["month"].startswith(str(year)):
                yearly_months.append(month_data)
                total_year_spending += month_data["total_spent"]
                total_year_transactions += month_data["transaction_count"]
                
                # Aggregate categories
                for category, amount in month_data["categories"].items():
                    all_categories[category] = all_categories.get(category, 0) + amount
        
        # Sort months chronologically
        yearly_months.sort(key=lambda x: x["month"])
        
        # Get top categories for the year
        top_categories = dict(sorted(all_categories.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "success": True,
            "message": f"Yearly overview for {year}",
            "data": {
                "year": year,
                "months": yearly_months,
                "summary": {
                    "total_spent": round(total_year_spending, 2),
                    "total_transactions": total_year_transactions,
                    "average_monthly_spending": round(total_year_spending / max(len(yearly_months), 1), 2),
                    "months_with_data": len(yearly_months),
                    "top_categories": top_categories
                }
            },
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get yearly overview: {str(e)}")
