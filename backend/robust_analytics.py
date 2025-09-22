"""
Robust analytics module replacing dummy data with real statistical analysis
"""
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
from data_validator import DataValidator
import logging

logger = logging.getLogger(__name__)

class RobustAnalytics:
    """Handles real analytics with proper error handling and outlier detection"""
    
    def __init__(self, db_path: str = "financial_copilot.db"):
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
    
    def get_spending_by_category(self) -> Dict[str, Any]:
        """Get real spending breakdown by category with validation"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get category spending with proper aggregation
                cursor.execute("""
                    SELECT 
                        COALESCE(category, 'other') as category,
                        COUNT(*) as transaction_count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount,
                        MIN(amount) as min_amount,
                        MAX(amount) as max_amount
                    FROM transactions 
                    WHERE transaction_type = 'debit' 
                    AND amount > 0
                    GROUP BY COALESCE(category, 'other')
                    ORDER BY total_amount DESC
                """)
                
                results = cursor.fetchall()
                
                if not results:
                    return {
                        'success': True,
                        'categories': [],
                        'total_spending': 0.0,
                        'category_count': 0,
                        'message': 'No spending data available'
                    }
                
                categories = []
                total_spending = 0.0
                
                for row in results:
                    category_data = [
                        row['category'],
                        float(row['total_amount']),
                        int(row['transaction_count']),
                        float(row['avg_amount']),
                        float(row['min_amount']),
                        float(row['max_amount'])
                    ]
                    categories.append(category_data)
                    total_spending += float(row['total_amount'])
                
                # Detect outlier categories
                amounts = [cat[1] for cat in categories]
                if len(amounts) > 2:
                    outlier_threshold = statistics.mean(amounts) + 2 * statistics.stdev(amounts)
                    for category in categories:
                        if category[1] > outlier_threshold:
                            category.append(True)  # is_outlier flag
                        else:
                            category.append(False)
                
                return {
                    'success': True,
                    'categories': categories,
                    'total_spending': total_spending,
                    'category_count': len(categories),
                    'analysis': {
                        'highest_spending_category': categories[0][0] if categories else None,
                        'lowest_spending_category': categories[-1][0] if categories else None,
                        'avg_category_spending': total_spending / len(categories) if categories else 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in get_spending_by_category: {e}")
            return {
                'success': False,
                'error': str(e),
                'categories': [],
                'total_spending': 0.0,
                'category_count': 0
            }
    
    def get_monthly_trends(self, months: int = 12) -> Dict[str, Any]:
        """Get real monthly spending trends with statistical analysis"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get monthly data for the specified period
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m', date) as month,
                        strftime('%Y', date) as year,
                        strftime('%m', date) as month_num,
                        COUNT(*) as transaction_count,
                        SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as total_spending,
                        SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as total_income,
                        AVG(CASE WHEN transaction_type = 'debit' THEN amount ELSE NULL END) as avg_spending
                    FROM transactions 
                    WHERE date >= date('now', '-{} months')
                    AND amount > 0
                    GROUP BY strftime('%Y-%m', date)
                    ORDER BY month DESC
                    LIMIT ?
                """.format(months), (months,))
                
                results = cursor.fetchall()
                
                if not results:
                    return {
                        'success': True,
                        'monthly_trends': [],
                        'trend_analysis': {'message': 'No data available for trend analysis'}
                    }
                
                monthly_data = []
                spending_amounts = []
                
                # Month names for display
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                
                for row in results:
                    month_num = int(row['month_num'])
                    month_name = month_names[month_num - 1]
                    
                    spending = float(row['total_spending'] or 0)
                    spending_amounts.append(spending)
                    
                    monthly_data.append({
                        'month': row['month'],
                        'month_name': month_name,
                        'year': row['year'],
                        'transaction_count': int(row['transaction_count']),
                        'total_spending': spending,
                        'total_income': float(row['total_income'] or 0),
                        'avg_spending': float(row['avg_spending'] or 0),
                        'net_flow': float(row['total_income'] or 0) - spending
                    })
                
                # Calculate trend analysis
                trend_analysis = self._calculate_trend_analysis(spending_amounts)
                
                return {
                    'success': True,
                    'monthly_trends': list(reversed(monthly_data)),  # Chronological order
                    'trend_analysis': trend_analysis,
                    'period_months': len(monthly_data)
                }
                
        except Exception as e:
            logger.error(f"Error in get_monthly_trends: {e}")
            return {
                'success': False,
                'error': str(e),
                'monthly_trends': [],
                'trend_analysis': {}
            }
    
    def get_spending_insights(self) -> Dict[str, Any]:
        """Generate comprehensive spending insights with real data"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Get comprehensive statistics
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_transactions,
                        SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as total_spending,
                        SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as total_income,
                        AVG(CASE WHEN transaction_type = 'debit' THEN amount ELSE NULL END) as avg_transaction,
                        MAX(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as max_spending,
                        MIN(CASE WHEN transaction_type = 'debit' AND amount > 0 THEN amount ELSE NULL END) as min_spending,
                        COUNT(DISTINCT vendor) as unique_vendors,
                        COUNT(DISTINCT date) as active_days
                    FROM transactions 
                    WHERE amount > 0
                """)
                
                row = cursor.fetchone()
                
                if not row or row['total_transactions'] == 0:
                    return {
                        'success': True,
                        'total_transactions': 0,
                        'total_spending': 0.0,
                        'total_income': 0.0,
                        'net_balance': 0.0,
                        'average_transaction': 0.0,
                        'insights': ['No transaction data available for analysis']
                    }
                
                total_spending = float(row['total_spending'] or 0)
                total_income = float(row['total_income'] or 0)
                net_balance = total_income - total_spending
                avg_transaction = float(row['avg_transaction'] or 0)
                
                # Generate insights
                insights = self._generate_spending_insights(
                    total_spending, total_income, avg_transaction,
                    row['unique_vendors'], row['active_days'], row['total_transactions']
                )
                
                return {
                    'success': True,
                    'total_transactions': int(row['total_transactions']),
                    'total_spending': total_spending,
                    'total_income': total_income,
                    'net_balance': net_balance,
                    'average_transaction': avg_transaction,
                    'max_spending': float(row['max_spending'] or 0),
                    'min_spending': float(row['min_spending'] or 0),
                    'unique_vendors': int(row['unique_vendors']),
                    'active_days': int(row['active_days']),
                    'insights': insights
                }
                
        except Exception as e:
            logger.error(f"Error in get_spending_insights: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_transactions': 0,
                'total_spending': 0.0,
                'total_income': 0.0,
                'net_balance': 0.0,
                'average_transaction': 0.0,
                'insights': [f'Error generating insights: {str(e)}']
            }
    
    def get_top_vendors(self, limit: int = 10) -> Dict[str, Any]:
        """Get top vendors by spending with real data validation"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        vendor,
                        COUNT(*) as transaction_count,
                        SUM(amount) as total_spending,
                        AVG(amount) as avg_spending,
                        MAX(amount) as max_spending,
                        MIN(amount) as min_spending,
                        MAX(date) as last_transaction
                    FROM transactions 
                    WHERE transaction_type = 'debit' 
                    AND amount > 0
                    AND vendor IS NOT NULL
                    AND vendor != ''
                    GROUP BY vendor
                    ORDER BY total_spending DESC
                    LIMIT ?
                """, (limit,))
                
                results = cursor.fetchall()
                
                if not results:
                    return {
                        'success': True,
                        'top_vendors': [],
                        'vendor_count': 0,
                        'message': 'No vendor data available'
                    }
                
                vendors = []
                for row in results:
                    vendor_data = {
                        'vendor': row['vendor'],
                        'transaction_count': int(row['transaction_count']),
                        'total_spending': float(row['total_spending']),
                        'avg_spending': float(row['avg_spending']),
                        'max_spending': float(row['max_spending']),
                        'min_spending': float(row['min_spending']),
                        'last_transaction': row['last_transaction']
                    }
                    vendors.append(vendor_data)
                
                return {
                    'success': True,
                    'top_vendors': vendors,
                    'vendor_count': len(vendors),
                    'analysis': {
                        'top_vendor': vendors[0]['vendor'] if vendors else None,
                        'total_vendors_spending': sum(v['total_spending'] for v in vendors)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in get_top_vendors: {e}")
            return {
                'success': False,
                'error': str(e),
                'top_vendors': [],
                'vendor_count': 0
            }
    
    def _calculate_trend_analysis(self, amounts: List[float]) -> Dict[str, Any]:
        """Calculate statistical trend analysis"""
        if len(amounts) < 2:
            return {'trend': 'insufficient_data'}
        
        try:
            # Calculate trend direction
            recent_avg = statistics.mean(amounts[:3]) if len(amounts) >= 3 else amounts[0]
            older_avg = statistics.mean(amounts[-3:]) if len(amounts) >= 3 else amounts[-1]
            
            trend_direction = 'increasing' if recent_avg > older_avg else 'decreasing'
            trend_strength = abs(recent_avg - older_avg) / older_avg if older_avg > 0 else 0
            
            # Calculate volatility
            volatility = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            return {
                'trend': trend_direction,
                'trend_strength': trend_strength,
                'volatility': volatility,
                'average': statistics.mean(amounts),
                'median': statistics.median(amounts),
                'max': max(amounts),
                'min': min(amounts)
            }
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {'trend': 'calculation_error', 'error': str(e)}
    
    def _generate_spending_insights(self, total_spending: float, total_income: float, 
                                  avg_transaction: float, unique_vendors: int, 
                                  active_days: int, total_transactions: int) -> List[str]:
        """Generate meaningful insights from spending data"""
        insights = []
        
        try:
            # Net balance insight
            if total_income > total_spending:
                surplus = total_income - total_spending
                insights.append(f"You have a surplus of ₹{surplus:.0f} this period")
            elif total_spending > total_income:
                deficit = total_spending - total_income
                insights.append(f"You spent ₹{deficit:.0f} more than your income")
            
            # Transaction frequency insight
            if active_days > 0:
                daily_avg = total_transactions / active_days
                insights.append(f"You make an average of {daily_avg:.1f} transactions per day")
            
            # Spending pattern insight
            if avg_transaction > 1000:
                insights.append("Your transactions tend to be high-value")
            elif avg_transaction < 100:
                insights.append("You mostly make small-value transactions")
            
            # Vendor diversity insight
            if unique_vendors > 20:
                insights.append("You have diverse spending across many vendors")
            elif unique_vendors < 5:
                insights.append("Your spending is concentrated among few vendors")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Unable to generate insights due to data processing error"]
