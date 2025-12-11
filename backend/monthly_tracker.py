"""
Monthly tracking module for organizing transactions by date and generating monthly insights
"""
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import calendar
import logging

logger = logging.getLogger(__name__)

class MonthlyTracker:
    """Handles monthly organization and tracking of transactions"""
    
    def __init__(self, db_path: str = "transactions.db"):
        self.db_path = db_path
    
    def _get_db_connection(self):
        """Get database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def get_monthly_summary(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Get comprehensive monthly summary for a specific month"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get month boundaries
                start_date = f"{year}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year + 1}-01-01"
                else:
                    end_date = f"{year}-{month + 1:02d}-01"
                
                # Get monthly transactions
                cursor.execute("""
                    SELECT 
                        transaction_type,
                        category,
                        COUNT(*) as count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount,
                        MIN(amount) as min_amount,
                        MAX(amount) as max_amount
                    FROM transactions 
                    WHERE date >= ? AND date < ?
                    GROUP BY transaction_type, category
                    ORDER BY total_amount DESC
                """, (start_date, end_date))
                
                results = cursor.fetchall()
                
                # Organize data
                monthly_data = {
                    'year': year,
                    'month': month,
                    'month_name': calendar.month_name[month],
                    'total_spending': 0.0,
                    'total_income': 0.0,
                    'net_balance': 0.0,
                    'transaction_count': 0,
                    'categories': {},
                    'daily_breakdown': self._get_daily_breakdown(year, month),
                    'top_spending_days': [],
                    'insights': []
                }
                
                for row in results:
                    transaction_type = row['transaction_type']
                    category = row['category'] or 'Others'
                    
                    if transaction_type == 'debit':
                        monthly_data['total_spending'] += float(row['total_amount'])
                    else:
                        monthly_data['total_income'] += float(row['total_amount'])
                    
                    monthly_data['transaction_count'] += int(row['count'])
                    
                    if category not in monthly_data['categories']:
                        monthly_data['categories'][category] = {
                            'debit': {'count': 0, 'amount': 0.0},
                            'credit': {'count': 0, 'amount': 0.0}
                        }
                    
                    monthly_data['categories'][category][transaction_type] = {
                        'count': int(row['count']),
                        'amount': float(row['total_amount']),
                        'avg_amount': float(row['avg_amount']),
                        'min_amount': float(row['min_amount']),
                        'max_amount': float(row['max_amount'])
                    }
                
                monthly_data['net_balance'] = monthly_data['total_income'] - monthly_data['total_spending']
                
                # Generate insights
                monthly_data['insights'] = self._generate_monthly_insights(monthly_data)
                
                return {
                    'success': True,
                    'data': monthly_data
                }
                
        except Exception as e:
            logger.error(f"Error getting monthly summary: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _get_daily_breakdown(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get daily spending breakdown for the month"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                start_date = f"{year}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year + 1}-01-01"
                else:
                    end_date = f"{year}-{month + 1:02d}-01"
                
                cursor.execute("""
                    SELECT 
                        DATE(date) as day,
                        transaction_type,
                        COUNT(*) as count,
                        SUM(amount) as total_amount
                    FROM transactions 
                    WHERE date >= ? AND date < ?
                    GROUP BY DATE(date), transaction_type
                    ORDER BY day
                """, (start_date, end_date))
                
                results = cursor.fetchall()
                
                # Organize by day
                daily_data = defaultdict(lambda: {'spending': 0.0, 'income': 0.0, 'transactions': 0})
                
                for row in results:
                    day = row['day']
                    transaction_type = row['transaction_type']
                    amount = float(row['total_amount'])
                    count = int(row['count'])
                    
                    if transaction_type == 'debit':
                        daily_data[day]['spending'] += amount
                    else:
                        daily_data[day]['income'] += amount
                    
                    daily_data[day]['transactions'] += count
                
                # Convert to list format
                daily_breakdown = []
                for day, data in sorted(daily_data.items()):
                    daily_breakdown.append({
                        'date': day,
                        'spending': data['spending'],
                        'income': data['income'],
                        'net': data['income'] - data['spending'],
                        'transactions': data['transactions']
                    })
                
                return daily_breakdown
                
        except Exception as e:
            logger.error(f"Error getting daily breakdown: {e}")
            return []
    
    def _generate_monthly_insights(self, monthly_data: Dict[str, Any]) -> List[str]:
        """Generate insights for the monthly data"""
        insights = []
        
        try:
            total_spending = monthly_data['total_spending']
            total_income = monthly_data['total_income']
            net_balance = monthly_data['net_balance']
            categories = monthly_data['categories']
            
            # Net balance insight
            if net_balance > 0:
                insights.append(f"💚 Positive balance: ₹{net_balance:.0f} saved this month")
            elif net_balance < 0:
                insights.append(f"⚠️ Deficit: ₹{abs(net_balance):.0f} overspent this month")
            else:
                insights.append("⚖️ Balanced month: Income equals spending")
            
            # Top spending category
            if categories:
                top_category = max(categories.items(), 
                                 key=lambda x: x[1].get('debit', {}).get('amount', 0))
                if top_category[1].get('debit', {}).get('amount', 0) > 0:
                    amount = top_category[1]['debit']['amount']
                    percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                    insights.append(f"🏆 Top spending: {top_category[0]} (₹{amount:.0f}, {percentage:.1f}%)")
            
            # Daily average
            if total_spending > 0:
                daily_avg = total_spending / 30  # Approximate monthly days
                insights.append(f"📊 Daily average spending: ₹{daily_avg:.0f}")
            
            # Transaction frequency
            transaction_count = monthly_data['transaction_count']
            if transaction_count > 0:
                insights.append(f"📱 Total transactions: {transaction_count}")
            
            # Spending pattern analysis
            if total_spending > 50000:
                insights.append("💸 High spending month - consider budget review")
            elif total_spending < 10000:
                insights.append("💰 Low spending month - great savings opportunity")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Unable to generate insights"]
    
    def get_yearly_overview(self, year: int = None) -> Dict[str, Any]:
        """Get yearly overview with monthly breakdowns"""
        if year is None:
            year = datetime.now().year
        
        try:
            yearly_data = {
                'year': year,
                'months': [],
                'total_spending': 0.0,
                'total_income': 0.0,
                'net_balance': 0.0,
                'best_month': None,
                'worst_month': None
            }
            
            monthly_balances = []
            
            for month in range(1, 13):
                monthly_summary = self.get_monthly_summary(year, month)
                if monthly_summary['success']:
                    month_data = monthly_summary['data']
                    yearly_data['months'].append(month_data)
                    yearly_data['total_spending'] += month_data['total_spending']
                    yearly_data['total_income'] += month_data['total_income']
                    
                    monthly_balances.append((month, month_data['net_balance']))
            
            yearly_data['net_balance'] = yearly_data['total_income'] - yearly_data['total_spending']
            
            # Find best and worst months
            if monthly_balances:
                yearly_data['best_month'] = max(monthly_balances, key=lambda x: x[1])
                yearly_data['worst_month'] = min(monthly_balances, key=lambda x: x[1])
            
            return {
                'success': True,
                'data': yearly_data
            }
            
        except Exception as e:
            logger.error(f"Error getting yearly overview: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def get_spending_trends(self, months: int = 6) -> Dict[str, Any]:
        """Get spending trends over the last N months"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get data for the last N months
                cursor.execute("""
                    SELECT 
                        strftime('%Y', date) as year,
                        strftime('%m', date) as month,
                        SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as spending,
                        SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as income,
                        COUNT(*) as transactions
                    FROM transactions 
                    WHERE date >= date('now', '-{} months')
                    GROUP BY strftime('%Y-%m', date)
                    ORDER BY year, month
                """.format(months))
                
                results = cursor.fetchall()
                
                trend_data = []
                spending_amounts = []
                
                for row in results:
                    month_data = {
                        'year': int(row['year']),
                        'month': int(row['month']),
                        'month_name': calendar.month_name[int(row['month'])],
                        'spending': float(row['spending']),
                        'income': float(row['income']),
                        'net_balance': float(row['income']) - float(row['spending']),
                        'transactions': int(row['transactions'])
                    }
                    trend_data.append(month_data)
                    spending_amounts.append(month_data['spending'])
                
                # Calculate trend direction
                trend_analysis = self._analyze_trend(spending_amounts)
                
                return {
                    'success': True,
                    'trends': trend_data,
                    'analysis': trend_analysis,
                    'period_months': len(trend_data)
                }
                
        except Exception as e:
            logger.error(f"Error getting spending trends: {e}")
            return {
                'success': False,
                'error': str(e),
                'trends': [],
                'analysis': {}
            }
    
    def _analyze_trend(self, amounts: List[float]) -> Dict[str, Any]:
        """Analyze spending trend from amounts"""
        if len(amounts) < 2:
            return {'trend': 'insufficient_data'}
        
        try:
            # Simple trend analysis
            recent_avg = sum(amounts[-3:]) / min(3, len(amounts))
            older_avg = sum(amounts[:3]) / min(3, len(amounts))
            
            if recent_avg > older_avg * 1.1:
                trend = 'increasing'
            elif recent_avg < older_avg * 0.9:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            # Calculate volatility
            if len(amounts) > 1:
                avg = sum(amounts) / len(amounts)
                variance = sum((x - avg) ** 2 for x in amounts) / len(amounts)
                volatility = variance ** 0.5
            else:
                volatility = 0
            
            return {
                'trend': trend,
                'recent_average': recent_avg,
                'older_average': older_avg,
                'volatility': volatility,
                'change_percentage': ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {'trend': 'error', 'error': str(e)}

# Global monthly tracker instance
monthly_tracker = MonthlyTracker()
