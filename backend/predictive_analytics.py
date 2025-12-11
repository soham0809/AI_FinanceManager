"""
AI-Powered Predictive Analytics for Financial Insights
Provides spending forecasts, savings recommendations, and budget alerts
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pickle
import os
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

@dataclass
class SpendingForecast:
    """Data class for spending forecast results"""
    category: str
    current_month_prediction: float
    next_month_prediction: float
    confidence_score: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    recommendation: str

@dataclass
class SavingsGoal:
    """Data class for savings goal tracking"""
    goal_id: str
    target_amount: float
    current_saved: float
    target_date: datetime
    monthly_required: float
    achievable: bool
    recommendation: str

@dataclass
class BudgetAlert:
    """Data class for budget alerts"""
    category: str
    current_spending: float
    budget_limit: float
    percentage_used: float
    alert_level: str  # 'low', 'medium', 'high', 'critical'
    message: str

class PredictiveAnalytics:
    """AI-powered predictive analytics engine"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_path = "predictive_models.pkl"
        self.load_models()
    
    def prepare_features(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML models"""
        if transactions_df.empty:
            return pd.DataFrame()
        
        # Convert date column
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        transactions_df = transactions_df.sort_values('date')
        
        # Create time-based features
        transactions_df['year'] = transactions_df['date'].dt.year
        transactions_df['month'] = transactions_df['date'].dt.month
        transactions_df['day'] = transactions_df['date'].dt.day
        transactions_df['day_of_week'] = transactions_df['date'].dt.dayofweek
        transactions_df['is_weekend'] = transactions_df['day_of_week'].isin([5, 6]).astype(int)
        
        # Create rolling averages
        transactions_df['amount_7d_avg'] = transactions_df['amount'].rolling(window=7, min_periods=1).mean()
        transactions_df['amount_30d_avg'] = transactions_df['amount'].rolling(window=30, min_periods=1).mean()
        
        # Create category-based features
        category_stats = transactions_df.groupby('category')['amount'].agg(['mean', 'std', 'count']).reset_index()
        category_stats.columns = ['category', 'category_mean', 'category_std', 'category_count']
        transactions_df = transactions_df.merge(category_stats, on='category', how='left')
        
        return transactions_df
    
    def train_spending_models(self, transactions_data: List[Dict]) -> Dict[str, float]:
        """Train predictive models for each spending category"""
        if not transactions_data:
            return {}
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions_data)
        df = df[df['transaction_type'] == 'debit']  # Only spending transactions
        
        if df.empty:
            return {}
        
        # Prepare features
        df = self.prepare_features(df)
        
        if df.empty:
            return {}
        
        model_scores = {}
        
        # Train model for each category
        categories = df['category'].unique()
        
        for category in categories:
            try:
                category_df = df[df['category'] == category].copy()
                
                if len(category_df) < 5:  # Need minimum data points
                    continue
                
                # Prepare features for this category
                feature_columns = ['year', 'month', 'day', 'day_of_week', 'is_weekend', 
                                 'amount_7d_avg', 'amount_30d_avg', 'category_mean', 'category_std']
                
                # Check if all feature columns exist
                available_features = [col for col in feature_columns if col in category_df.columns]
                
                if not available_features:
                    continue
                
                X = category_df[available_features].fillna(0)
                y = category_df['amount']
                
                if len(X) < 3:
                    continue
                
                # Scale features
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Train Random Forest model
                model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5)
                model.fit(X_scaled, y)
                
                # Calculate model score
                y_pred = model.predict(X_scaled)
                mae = mean_absolute_error(y, y_pred)
                
                # Store model and scaler
                self.models[category] = model
                self.scalers[category] = scaler
                model_scores[category] = mae
                
            except Exception as e:
                print(f"Error training model for {category}: {e}")
                continue
        
        # Save models
        self.save_models()
        
        return model_scores
    
    def predict_spending(self, category: str, target_date: datetime = None) -> Optional[SpendingForecast]:
        """Predict spending for a specific category"""
        if category not in self.models:
            return None
        
        if target_date is None:
            target_date = datetime.now() + timedelta(days=30)
        
        try:
            # Prepare features for prediction
            features = np.array([[
                target_date.year,
                target_date.month,
                target_date.day,
                target_date.weekday(),
                1 if target_date.weekday() >= 5 else 0,
                0,  # amount_7d_avg (placeholder)
                0,  # amount_30d_avg (placeholder)
                0,  # category_mean (placeholder)
                0   # category_std (placeholder)
            ]])
            
            # Scale features
            features_scaled = self.scalers[category].transform(features)
            
            # Make prediction
            prediction = self.models[category].predict(features_scaled)[0]
            
            # Calculate confidence score (simplified)
            confidence = min(0.95, max(0.3, 0.8 - (abs(prediction) / 10000) * 0.1))
            
            # Determine trend (simplified)
            trend = "stable"
            if prediction > 1000:
                trend = "increasing"
            elif prediction < 500:
                trend = "decreasing"
            
            # Generate recommendation
            recommendation = self._generate_spending_recommendation(category, prediction, trend)
            
            return SpendingForecast(
                category=category,
                current_month_prediction=prediction,
                next_month_prediction=prediction * 1.05,  # Slight increase assumption
                confidence_score=confidence,
                trend=trend,
                recommendation=recommendation
            )
            
        except Exception as e:
            print(f"Error predicting spending for {category}: {e}")
            return None
    
    def _generate_spending_recommendation(self, category: str, prediction: float, trend: str) -> str:
        """Generate personalized spending recommendations"""
        recommendations = {
            'Food & Dining': {
                'increasing': f"Your {category} spending is trending up (₹{prediction:.0f}). Consider meal planning and cooking at home more often.",
                'decreasing': f"Great job reducing {category} expenses! Keep up the good work with home cooking.",
                'stable': f"Your {category} spending is stable at ₹{prediction:.0f}. Consider setting a monthly budget to optimize further."
            },
            'Shopping': {
                'increasing': f"Shopping expenses are rising (₹{prediction:.0f}). Try the 24-hour rule before making non-essential purchases.",
                'decreasing': f"You're doing well controlling shopping expenses. Consider investing the saved money.",
                'stable': f"Shopping spending is consistent at ₹{prediction:.0f}. Focus on needs vs wants to optimize further."
            },
            'Transportation': {
                'increasing': f"Transportation costs are increasing (₹{prediction:.0f}). Consider carpooling or public transport options.",
                'decreasing': f"Good job reducing transportation expenses! Keep exploring cost-effective travel options.",
                'stable': f"Transportation spending is steady at ₹{prediction:.0f}. Look for monthly passes or bulk booking discounts."
            },
            'Entertainment': {
                'increasing': f"Entertainment spending is up (₹{prediction:.0f}). Look for free events and student discounts.",
                'decreasing': f"You're managing entertainment expenses well. Balance is key for a healthy lifestyle.",
                'stable': f"Entertainment budget is stable at ₹{prediction:.0f}. Consider setting a monthly entertainment allowance."
            }
        }
        
        default_rec = {
            'increasing': f"Spending in {category} is trending upward (₹{prediction:.0f}). Consider setting a monthly budget limit.",
            'decreasing': f"You're doing well managing {category} expenses. Keep up the good financial habits!",
            'stable': f"Your {category} spending is stable at ₹{prediction:.0f}. Monitor regularly to maintain control."
        }
        
        return recommendations.get(category, default_rec)[trend]
    
    def create_savings_goal(self, target_amount: float, target_months: int, 
                          current_income: float, current_expenses: float) -> SavingsGoal:
        """Create and analyze a savings goal"""
        target_date = datetime.now() + timedelta(days=target_months * 30)
        monthly_surplus = current_income - current_expenses
        monthly_required = target_amount / target_months
        
        achievable = monthly_required <= monthly_surplus * 0.8  # 80% of surplus for safety
        
        if achievable:
            recommendation = f"This goal is achievable! Save ₹{monthly_required:.0f} monthly from your ₹{monthly_surplus:.0f} surplus."
        else:
            needed_reduction = monthly_required - (monthly_surplus * 0.8)
            recommendation = f"Challenging goal. Consider reducing expenses by ₹{needed_reduction:.0f}/month or extending timeline."
        
        return SavingsGoal(
            goal_id=f"goal_{int(datetime.now().timestamp())}",
            target_amount=target_amount,
            current_saved=0.0,
            target_date=target_date,
            monthly_required=monthly_required,
            achievable=achievable,
            recommendation=recommendation
        )
    
    def generate_budget_alerts(self, current_spending: Dict[str, float], 
                             budget_limits: Dict[str, float]) -> List[BudgetAlert]:
        """Generate budget alerts based on current spending vs limits"""
        alerts = []
        
        for category, spending in current_spending.items():
            if category not in budget_limits:
                continue
            
            limit = budget_limits[category]
            percentage = (spending / limit) * 100 if limit > 0 else 0
            
            # Determine alert level
            if percentage >= 100:
                alert_level = "critical"
                message = f"Budget exceeded! You've spent ₹{spending:.0f} of ₹{limit:.0f} limit."
            elif percentage >= 80:
                alert_level = "high"
                message = f"Approaching budget limit. ₹{limit - spending:.0f} remaining this month."
            elif percentage >= 60:
                alert_level = "medium"
                message = f"60% of budget used. ₹{limit - spending:.0f} left for {category}."
            else:
                alert_level = "low"
                message = f"On track! ₹{limit - spending:.0f} remaining in {category} budget."
            
            alerts.append(BudgetAlert(
                category=category,
                current_spending=spending,
                budget_limit=limit,
                percentage_used=percentage,
                alert_level=alert_level,
                message=message
            ))
        
        return alerts
    
    def get_financial_insights(self, transactions_data: List[Dict]) -> Dict[str, str]:
        """Generate personalized financial insights"""
        if not transactions_data:
            return {"message": "No transaction data available for insights."}
        
        df = pd.DataFrame(transactions_data)
        spending_df = df[df['transaction_type'] == 'debit']
        
        if spending_df.empty:
            return {"message": "No spending data available for insights."}
        
        insights = {}
        
        # Top spending category
        top_category = spending_df.groupby('category')['amount'].sum().idxmax()
        top_amount = spending_df.groupby('category')['amount'].sum().max()
        insights['top_category'] = f"Your highest spending category is {top_category} (₹{top_amount:.0f})"
        
        # Average transaction
        avg_transaction = spending_df['amount'].mean()
        insights['avg_transaction'] = f"Your average transaction is ₹{avg_transaction:.0f}"
        
        # Spending frequency
        daily_transactions = len(spending_df) / 30  # Assuming last 30 days
        insights['frequency'] = f"You make approximately {daily_transactions:.1f} transactions per day"
        
        # Weekend vs weekday spending (if date parsing works)
        try:
            spending_df['date'] = pd.to_datetime(spending_df['date'])
            spending_df['is_weekend'] = spending_df['date'].dt.dayofweek.isin([5, 6])
            weekend_avg = spending_df[spending_df['is_weekend']]['amount'].mean()
            weekday_avg = spending_df[~spending_df['is_weekend']]['amount'].mean()
            
            if weekend_avg > weekday_avg:
                insights['weekend_pattern'] = f"You spend {((weekend_avg/weekday_avg - 1) * 100):.0f}% more on weekends"
            else:
                insights['weekend_pattern'] = "You spend more on weekdays than weekends"
        except:
            insights['weekend_pattern'] = "Weekend spending pattern analysis unavailable"
        
        return insights
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'timestamp': datetime.now()
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.models = model_data.get('models', {})
                    self.scalers = model_data.get('scalers', {})
        except Exception as e:
            print(f"Error loading models: {e}")
            self.models = {}
            self.scalers = {}

# Global predictive analytics instance
predictive_engine = PredictiveAnalytics()
