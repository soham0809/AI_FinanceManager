"""Analytics routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Dict, Any, List
from app.config.database import get_db
from app.models.transaction import Transaction
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])

@router.get("/insights")
async def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get financial insights for user"""
    # Get user's transactions
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    
    if not transactions:
        return {
            "success": True,
            "total_transactions": 0,
            "total_spending": 0.0,
            "total_income": 0.0,
            "net_balance": 0.0,
            "insights": ["No transactions found"]
        }
    
    # Calculate metrics using transaction_type
    total_transactions = len(transactions)
    total_spending = sum(t.amount for t in transactions if t.transaction_type == 'debit')
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'credit')
    net_balance = total_income - total_spending
    
    spending_transactions = [t for t in transactions if t.transaction_type == 'debit']
    avg_transaction = total_spending / len(spending_transactions) if spending_transactions else 0
    max_spending = max((t.amount for t in spending_transactions), default=0)
    min_spending = min((t.amount for t in spending_transactions), default=0)
    
    # Get unique vendors and active days
    unique_vendors = len(set(t.vendor for t in transactions))
    unique_dates = len(set(t.date.date() if t.date else None for t in transactions if t.date))
    
    # Generate insights
    insights = []
    if net_balance < 0:
        insights.append(f"You spent ₹{abs(net_balance):.0f} more than your income")
    else:
        insights.append(f"You saved ₹{net_balance:.0f} this period")
    
    if unique_dates > 0:
        avg_per_day = total_transactions / unique_dates
        insights.append(f"You make an average of {avg_per_day:.1f} transactions per day")
    
    if avg_transaction > 1000:
        insights.append("Your transactions tend to be high-value")
    
    return {
        "success": True,
        "total_transactions": total_transactions,
        "total_spending": total_spending,
        "total_income": total_income,
        "net_balance": net_balance,
        "average_transaction": avg_transaction,
        "max_spending": max_spending,
        "min_spending": min_spending,
        "unique_vendors": unique_vendors,
        "active_days": unique_dates,
        "insights": insights
    }

@router.get("/insights-public")
async def get_insights_public(db: Session = Depends(get_db)):
    """Get financial insights for all transactions (backward compatibility)"""
    transactions = db.query(Transaction).all()
    
    if not transactions:
        return {
            "success": True,
            "total_transactions": 0,
            "total_spending": 0.0,
            "total_income": 0.0,
            "net_balance": 0.0,
            "insights": ["No transactions found"]
        }
    
    # Calculate metrics using transaction_type
    total_transactions = len(transactions)
    total_spending = sum(t.amount for t in transactions if t.transaction_type == 'debit')
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'credit')
    net_balance = total_income - total_spending
    
    spending_transactions = [t for t in transactions if t.transaction_type == 'debit']
    avg_transaction = total_spending / len(spending_transactions) if spending_transactions else 0
    max_spending = max((t.amount for t in spending_transactions), default=0)
    min_spending = min((t.amount for t in spending_transactions), default=0)
    
    # Get unique vendors and active days
    unique_vendors = len(set(t.vendor for t in transactions))
    unique_dates = len(set(t.date.date() if t.date else None for t in transactions if t.date))
    
    # Generate insights
    insights = []
    if net_balance < 0:
        insights.append(f"You spent ₹{abs(net_balance):.0f} more than your income")
    else:
        insights.append(f"You saved ₹{net_balance:.0f} this period")
    
    if unique_dates > 0:
        avg_per_day = total_transactions / unique_dates
        insights.append(f"You make an average of {avg_per_day:.1f} transactions per day")
    
    if avg_transaction > 1000:
        insights.append("Your transactions tend to be high-value")
    
    return {
        "success": True,
        "total_transactions": total_transactions,
        "total_spending": total_spending,
        "total_income": total_income,
        "net_balance": net_balance,
        "average_transaction": avg_transaction,
        "max_spending": max_spending,
        "min_spending": min_spending,
        "unique_vendors": unique_vendors,
        "active_days": unique_dates,
        "insights": insights
    }

@router.get("/spending-by-category")
async def get_spending_by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get spending breakdown by category"""
    # Query spending by category using transaction_type
    category_spending = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count'),
        func.avg(Transaction.amount).label('avg_amount'),
        func.min(Transaction.amount).label('min_amount'),
        func.max(Transaction.amount).label('max_amount')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'debit'
    ).group_by(Transaction.category).all()
    
    categories = {}
    total_spending = 0
    
    for cat in category_spending:
        categories[cat.category] = {
            'total_amount': float(cat.total_amount),
            'transaction_count': cat.transaction_count,
            'avg_amount': float(cat.avg_amount),
            'min_amount': float(cat.min_amount),
            'max_amount': float(cat.max_amount),
            'is_high_spending': cat.total_amount > 5000
        }
        total_spending += cat.total_amount
    
    # Analysis
    if categories:
        highest_category = max(categories.keys(), key=lambda k: categories[k]['total_amount'])
        lowest_category = min(categories.keys(), key=lambda k: categories[k]['total_amount'])
        avg_category_spending = total_spending / len(categories)
    else:
        highest_category = None
        lowest_category = None
        avg_category_spending = 0
    
    return {
        "success": True,
        "categories": categories,
        "total_spending": total_spending,
        "category_count": len(categories),
        "analysis": {
            "highest_spending_category": highest_category,
            "lowest_spending_category": lowest_category,
            "avg_category_spending": avg_category_spending
        }
    }

@router.get("/spending-by-category-public")
async def get_spending_by_category_public(db: Session = Depends(get_db)):
    """Get spending breakdown by category (backward compatibility)"""
    # Query spending by category using transaction_type
    category_spending = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count'),
        func.avg(Transaction.amount).label('avg_amount'),
        func.min(Transaction.amount).label('min_amount'),
        func.max(Transaction.amount).label('max_amount')
    ).filter(
        Transaction.transaction_type == 'debit'
    ).group_by(Transaction.category).all()
    
    categories = {}
    total_spending = 0
    
    for cat in category_spending:
        categories[cat.category] = {
            'total_amount': float(cat.total_amount),
            'transaction_count': cat.transaction_count,
            'avg_amount': float(cat.avg_amount),
            'min_amount': float(cat.min_amount),
            'max_amount': float(cat.max_amount),
            'is_high_spending': cat.total_amount > 5000
        }
        total_spending += cat.total_amount
    
    # Analysis
    if categories:
        highest_category = max(categories.keys(), key=lambda k: categories[k]['total_amount'])
        lowest_category = min(categories.keys(), key=lambda k: categories[k]['total_amount'])
        avg_category_spending = total_spending / len(categories)
    else:
        highest_category = None
        lowest_category = None
        avg_category_spending = 0
    
    return {
        "success": True,
        "categories": categories,
        "total_spending": total_spending,
        "category_count": len(categories),
        "analysis": {
            "highest_spending_category": highest_category,
            "lowest_spending_category": lowest_category,
            "avg_category_spending": avg_category_spending
        }
    }

@router.get("/monthly-trends")
async def get_monthly_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get monthly spending trends"""
    # Use strftime for SQLite date handling
    monthly_data = db.query(
        func.strftime('%Y', Transaction.date).label('year'),
        func.strftime('%m', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'debit'
    ).group_by(
        func.strftime('%Y', Transaction.date),
        func.strftime('%m', Transaction.date)
    ).order_by('year', 'month').all()
    
    monthly_trends = {}
    for data in monthly_data:
        month_key = f"{int(data.year)}-{int(data.month):02d}"
        monthly_trends[month_key] = {
            'total_spending': float(data.total_amount),
            'transaction_count': data.transaction_count
        }
    
    # Trend analysis
    if len(monthly_trends) < 2:
        trend_analysis = {"message": "No data available for trend analysis"}
    else:
        # Simple trend analysis
        values = list(monthly_trends.values())
        recent_spending = values[-1]['total_spending']
        previous_spending = values[-2]['total_spending']
        
        if recent_spending > previous_spending:
            trend = "increasing"
            change = ((recent_spending - previous_spending) / previous_spending) * 100
        else:
            trend = "decreasing"
            change = ((previous_spending - recent_spending) / previous_spending) * 100
        
        trend_analysis = {
            "trend": trend,
            "change_percentage": round(change, 2),
            "message": f"Spending is {trend} by {change:.1f}%"
        }
    
    return {
        "success": True,
        "monthly_trends": monthly_trends,
        "trend_analysis": trend_analysis
    }

@router.get("/monthly-trends-public")
async def get_monthly_trends_public(db: Session = Depends(get_db)):
    """Get monthly spending trends (backward compatibility)"""
    # Use strftime for SQLite date handling
    monthly_data = db.query(
        func.strftime('%Y', Transaction.date).label('year'),
        func.strftime('%m', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count')
    ).filter(
        Transaction.transaction_type == 'debit'
    ).group_by(
        func.strftime('%Y', Transaction.date),
        func.strftime('%m', Transaction.date)
    ).order_by('year', 'month').all()
    
    monthly_trends = {}
    for data in monthly_data:
        month_key = f"{int(data.year)}-{int(data.month):02d}"
        monthly_trends[month_key] = {
            'total_spending': float(data.total_amount),
            'transaction_count': data.transaction_count
        }
    
    # Trend analysis
    if len(monthly_trends) < 2:
        trend_analysis = {"message": "No data available for trend analysis"}
    else:
        # Simple trend analysis
        values = list(monthly_trends.values())
        recent_spending = values[-1]['total_spending']
        previous_spending = values[-2]['total_spending']
        
        if recent_spending > previous_spending:
            trend = "increasing"
            change = ((recent_spending - previous_spending) / previous_spending) * 100
        else:
            trend = "decreasing"
            change = ((previous_spending - recent_spending) / previous_spending) * 100
        
        trend_analysis = {
            "trend": trend,
            "change_percentage": round(change, 2),
            "message": f"Spending is {trend} by {change:.1f}%"
        }
    
    return {
        "success": True,
        "monthly_trends": monthly_trends,
        "trend_analysis": trend_analysis
    }

@router.get("/top-vendors")
async def get_top_vendors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 10
):
    """Get top vendors by spending"""
    top_vendors = db.query(
        Transaction.vendor,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count'),
        func.avg(Transaction.amount).label('avg_amount')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == 'debit'
    ).group_by(Transaction.vendor).order_by(
        func.sum(Transaction.amount).desc()
    ).limit(limit).all()
    
    vendors = []
    for vendor in top_vendors:
        vendors.append({
            'vendor': vendor.vendor,
            'total_spending': float(vendor.total_amount),
            'transaction_count': vendor.transaction_count,
            'avg_spending': float(vendor.avg_amount)
        })
    
    return {
        "success": True,
        "top_vendors": vendors,
        "vendor_count": len(vendors)
    }

@router.get("/top-vendors-public")
async def get_top_vendors_public(db: Session = Depends(get_db), limit: int = 10):
    """Get top vendors by spending (backward compatibility)"""
    top_vendors = db.query(
        Transaction.vendor,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count'),
        func.avg(Transaction.amount).label('avg_amount')
    ).filter(
        Transaction.transaction_type == 'debit'
    ).group_by(Transaction.vendor).order_by(
        func.sum(Transaction.amount).desc()
    ).limit(limit).all()
    
    vendors = []
    for vendor in top_vendors:
        vendors.append({
            'vendor': vendor.vendor,
            'total_spending': float(vendor.total_amount),
            'transaction_count': vendor.transaction_count,
            'avg_spending': float(vendor.avg_amount)
        })
    
    return {
        "success": True,
        "top_vendors": vendors,
        "vendor_count": len(vendors)
    }
