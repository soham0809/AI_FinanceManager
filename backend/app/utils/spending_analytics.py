"""
Spending Analytics - Monthly and Weekly spending analysis
WITHOUT modifying existing database
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from collections import defaultdict
import calendar

class SpendingAnalytics:
    def __init__(self):
        pass
    
    def get_monthly_spending(self, db: Session, user_id: int, months: int = 6) -> Dict[str, Any]:
        """Get monthly spending breakdown for the last N months"""
        
        # Get all user transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()
        
        if not transactions:
            return {"error": "No transactions found"}
        
        # Group by month
        monthly_data = defaultdict(lambda: {
            "total_spent": 0.0,
            "transaction_count": 0,
            "categories": defaultdict(float),
            "vendors": defaultdict(float),
            "transactions": []
        })
        
        current_date = datetime.now()
        
        for transaction in transactions:
            # Parse transaction date
            try:
                if transaction.date:
                    if isinstance(transaction.date, str):
                        # Try different date formats
                        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']:
                            try:
                                tx_date = datetime.strptime(transaction.date, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            # If no format works, use created_at
                            tx_date = transaction.created_at or current_date
                    else:
                        tx_date = transaction.date
                else:
                    tx_date = transaction.created_at or current_date
            except:
                tx_date = transaction.created_at or current_date
            
            # Create month key
            month_key = tx_date.strftime("%Y-%m")
            month_name = tx_date.strftime("%B %Y")
            
            # Only include debit transactions for spending
            if transaction.amount and transaction.amount > 0:
                # Check if it's a debit (spending) transaction
                is_debit = True
                if hasattr(transaction, 'transaction_type'):
                    is_debit = transaction.transaction_type == 'debit'
                elif transaction.sms_text:
                    # Heuristic: if SMS contains "credited", it's income, not spending
                    is_debit = 'credited' not in transaction.sms_text.lower()
                
                if is_debit:
                    monthly_data[month_key]["total_spent"] += transaction.amount
                    monthly_data[month_key]["transaction_count"] += 1
                    monthly_data[month_key]["month_name"] = month_name
                    
                    # Category breakdown
                    category = transaction.category or "Others"
                    monthly_data[month_key]["categories"][category] += transaction.amount
                    
                    # Vendor breakdown
                    vendor = transaction.vendor or "Unknown"
                    monthly_data[month_key]["vendors"][vendor] += transaction.amount
                    
                    # Add transaction details
                    monthly_data[month_key]["transactions"].append({
                        "vendor": vendor,
                        "amount": transaction.amount,
                        "category": category,
                        "date": tx_date.strftime("%Y-%m-%d")
                    })
        
        # Convert to sorted list
        sorted_months = []
        for month_key in sorted(monthly_data.keys(), reverse=True)[:months]:
            month_info = monthly_data[month_key]
            
            # Convert defaultdicts to regular dicts and sort
            categories = dict(sorted(month_info["categories"].items(), 
                                   key=lambda x: x[1], reverse=True))
            vendors = dict(sorted(month_info["vendors"].items(), 
                                key=lambda x: x[1], reverse=True)[:10])  # Top 10 vendors
            
            sorted_months.append({
                "month": month_key,
                "month_name": month_info["month_name"],
                "total_spent": round(month_info["total_spent"], 2),
                "transaction_count": month_info["transaction_count"],
                "categories": categories,
                "top_vendors": vendors,
                "transactions": month_info["transactions"][:10]  # Latest 10 transactions
            })
        
        return {
            "monthly_spending": sorted_months,
            "summary": {
                "total_months": len(sorted_months),
                "average_monthly_spending": round(sum(m["total_spent"] for m in sorted_months) / len(sorted_months), 2) if sorted_months else 0,
                "highest_spending_month": max(sorted_months, key=lambda x: x["total_spent"]) if sorted_months else None,
                "total_transactions": sum(m["transaction_count"] for m in sorted_months)
            }
        }
    
    def get_weekly_spending(self, db: Session, user_id: int, weeks: int = 8) -> Dict[str, Any]:
        """Get weekly spending breakdown for the last N weeks"""
        
        # Get all user transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()
        
        if not transactions:
            return {"error": "No transactions found"}
        
        # Group by week
        weekly_data = defaultdict(lambda: {
            "total_spent": 0.0,
            "transaction_count": 0,
            "categories": defaultdict(float),
            "daily_spending": defaultdict(float),
            "transactions": []
        })
        
        current_date = datetime.now()
        
        for transaction in transactions:
            # Parse transaction date
            try:
                if transaction.date:
                    if isinstance(transaction.date, str):
                        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']:
                            try:
                                tx_date = datetime.strptime(transaction.date, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            tx_date = transaction.created_at or current_date
                    else:
                        tx_date = transaction.date
                else:
                    tx_date = transaction.created_at or current_date
            except:
                tx_date = transaction.created_at or current_date
            
            # Get week start (Monday)
            days_since_monday = tx_date.weekday()
            week_start = tx_date - timedelta(days=days_since_monday)
            week_key = week_start.strftime("%Y-W%U")
            week_range = f"{week_start.strftime('%b %d')} - {(week_start + timedelta(days=6)).strftime('%b %d, %Y')}"
            
            # Only include debit transactions for spending
            if transaction.amount and transaction.amount > 0:
                is_debit = True
                if hasattr(transaction, 'transaction_type'):
                    is_debit = transaction.transaction_type == 'debit'
                elif transaction.sms_text:
                    is_debit = 'credited' not in transaction.sms_text.lower()
                
                if is_debit:
                    weekly_data[week_key]["total_spent"] += transaction.amount
                    weekly_data[week_key]["transaction_count"] += 1
                    weekly_data[week_key]["week_range"] = week_range
                    weekly_data[week_key]["week_start"] = week_start.strftime("%Y-%m-%d")
                    
                    # Category breakdown
                    category = transaction.category or "Others"
                    weekly_data[week_key]["categories"][category] += transaction.amount
                    
                    # Daily spending within the week
                    day_name = tx_date.strftime("%A")
                    weekly_data[week_key]["daily_spending"][day_name] += transaction.amount
                    
                    # Add transaction details
                    weekly_data[week_key]["transactions"].append({
                        "vendor": transaction.vendor or "Unknown",
                        "amount": transaction.amount,
                        "category": category,
                        "date": tx_date.strftime("%Y-%m-%d"),
                        "day": day_name
                    })
        
        # Convert to sorted list
        sorted_weeks = []
        for week_key in sorted(weekly_data.keys(), reverse=True)[:weeks]:
            week_info = weekly_data[week_key]
            
            # Convert defaultdicts to regular dicts
            categories = dict(sorted(week_info["categories"].items(), 
                                   key=lambda x: x[1], reverse=True))
            daily_spending = dict(week_info["daily_spending"])
            
            sorted_weeks.append({
                "week": week_key,
                "week_range": week_info["week_range"],
                "week_start": week_info["week_start"],
                "total_spent": round(week_info["total_spent"], 2),
                "transaction_count": week_info["transaction_count"],
                "categories": categories,
                "daily_spending": daily_spending,
                "transactions": week_info["transactions"][:15]  # Latest 15 transactions
            })
        
        return {
            "weekly_spending": sorted_weeks,
            "summary": {
                "total_weeks": len(sorted_weeks),
                "average_weekly_spending": round(sum(w["total_spent"] for w in sorted_weeks) / len(sorted_weeks), 2) if sorted_weeks else 0,
                "highest_spending_week": max(sorted_weeks, key=lambda x: x["total_spent"]) if sorted_weeks else None,
                "total_transactions": sum(w["transaction_count"] for w in sorted_weeks)
            }
        }
    
    def get_spending_trends(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get spending trends and insights"""
        
        monthly_data = self.get_monthly_spending(db, user_id, 6)
        weekly_data = self.get_weekly_spending(db, user_id, 4)
        
        if "error" in monthly_data or "error" in weekly_data:
            return {"error": "Insufficient data for trends"}
        
        # Calculate trends
        monthly_spending = monthly_data["monthly_spending"]
        weekly_spending = weekly_data["weekly_spending"]
        
        trends = {
            "monthly_trend": "stable",
            "weekly_trend": "stable",
            "insights": []
        }
        
        # Monthly trend
        if len(monthly_spending) >= 2:
            recent_month = monthly_spending[0]["total_spent"]
            previous_month = monthly_spending[1]["total_spent"]
            
            if recent_month > previous_month * 1.1:
                trends["monthly_trend"] = "increasing"
                trends["insights"].append(f"Monthly spending increased by {round(((recent_month/previous_month - 1) * 100), 1)}%")
            elif recent_month < previous_month * 0.9:
                trends["monthly_trend"] = "decreasing"
                trends["insights"].append(f"Monthly spending decreased by {round(((1 - recent_month/previous_month) * 100), 1)}%")
        
        # Weekly trend
        if len(weekly_spending) >= 2:
            recent_week = weekly_spending[0]["total_spent"]
            previous_week = weekly_spending[1]["total_spent"]
            
            if recent_week > previous_week * 1.2:
                trends["weekly_trend"] = "increasing"
                trends["insights"].append(f"Weekly spending spiked by {round(((recent_week/previous_week - 1) * 100), 1)}%")
            elif recent_week < previous_week * 0.8:
                trends["weekly_trend"] = "decreasing"
                trends["insights"].append(f"Weekly spending dropped by {round(((1 - recent_week/previous_week) * 100), 1)}%")
        
        return trends
