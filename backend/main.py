from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import re
import json
from sms_parser import sms_parser
from database import DatabaseManager
from ml_categorizer import MLCategorizer
from predictive_analytics import PredictiveAnalytics
from group_expenses import GroupExpenseManager
from robust_analytics import RobustAnalytics
from monthly_tracker import monthly_tracker
from gemini_integration import gemini_assistant, initialize_gemini
from transaction_deduplicator import transaction_deduplicator
from sqlalchemy.orm import Session
import os

def get_db():
    """Database dependency"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize components
db_manager = DatabaseManager()
ml_categorizer = MLCategorizer()
predictive_engine = PredictiveAnalytics()
group_manager = GroupExpenseManager()
robust_analytics = RobustAnalytics()

# Initialize Gemini AI (use provided API key)
GEMINI_API_KEY = "AIzaSyCzL3_QfDj9PKBGGoycG8KqQWiuOEqnAnE"
initialize_gemini(GEMINI_API_KEY)

app = FastAPI(
    title="AI Financial Co-Pilot API",
    description="Backend API for the AI-powered financial assistant",
    version="1.0.0"
)

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SMSParseRequest(BaseModel):
    sms_text: str

class TransactionResponse(BaseModel):
    vendor: str
    amount: float
    date: str
    transaction_type: str  # "debit" or "credit"
    category: Optional[str] = None
    success: bool = True
    raw_text: str
    confidence: float = 0.0

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str

# Database is now initialized in database.py

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="AI Financial Co-Pilot API is running!",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        timestamp=datetime.now().isoformat()
    )

@app.post("/v1/parse-sms", response_model=TransactionResponse)
async def parse_sms(request: SMSParseRequest):
    """
    Parse transaction SMS and extract structured data using Gemini AI
    """
    try:
        # First try Gemini AI parsing for intelligent extraction
        if gemini_assistant and gemini_assistant.initialized:
            gemini_result = gemini_assistant.parse_sms_transaction(request.sms_text)
            
            if gemini_result['success']:
                transaction_data = gemini_result['transaction_data']
                
                # Format date properly if provided
                if transaction_data.get('date') and transaction_data['date'] != 'null':
                    try:
                        gemini_date = transaction_data.get('date')
                        if gemini_date and gemini_date != 'null':
                            try:
                                date_formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d/%m/%y']
                                parsed_date = None
                                
                                for fmt in date_formats:
                                    try:
                                        parsed_date = datetime.strptime(gemini_date, fmt)
                                        # Fix 2-digit year interpretation
                                        if fmt in ['%d-%m-%y', '%d/%m/%y']:
                                            # For 2-digit years, ensure they're in reasonable range (2020-2030)
                                            if parsed_date.year > 2030:
                                                parsed_date = parsed_date.replace(year=parsed_date.year - 100)
                                            elif parsed_date.year < 2020:
                                                parsed_date = parsed_date.replace(year=parsed_date.year + 100)
                                        break
                                    except ValueError:
                                        continue
                                
                                if parsed_date:
                                    current_date = datetime.now()
                                    if parsed_date > current_date:
                                        date_str = current_date.strftime('%Y-%m-%d')
                                    elif parsed_date < datetime(2020, 1, 1):
                                        date_str = current_date.strftime('%Y-%m-%d')
                                    else:
                                        date_str = parsed_date.strftime('%Y-%m-%d')
                                else:
                                    date_str = datetime.now().strftime('%Y-%m-%d')
                            except ValueError:
                                date_str = datetime.now().strftime('%Y-%m-%d')
                        else:
                            date_str = datetime.now().strftime('%Y-%m-%d')
                    except ValueError:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                else:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                
                # Prepare transaction data for duplicate detection
                duplicate_check_data = {
                    'vendor': transaction_data.get('vendor', 'Unknown'),
                    'amount': float(transaction_data['amount']),
                    'date': date_str,
                    'transaction_type': transaction_data.get('transaction_type', 'debit'),
                    'category': transaction_data.get('category', 'Others'),
                    'transaction_id': transaction_data.get('transaction_id')
                }
                
                # Apply confidence threshold filtering
                confidence_score = float(transaction_data.get('confidence', 0.0))
                if confidence_score < 0.7:  # Minimum confidence threshold
                    raise ValueError(f"Low confidence transaction ({confidence_score:.2f}). Likely not a valid transaction.")
                
                # Check for duplicates
                duplicate_result = transaction_deduplicator.is_duplicate(duplicate_check_data)
                
                if duplicate_result['is_duplicate']:
                    raise ValueError(f"Duplicate transaction detected: {duplicate_result['reason']}")
                
                # Prepare transaction data for database
                db_transaction_data = {
                    'vendor': transaction_data.get('vendor', 'Unknown'),
                    'amount': float(transaction_data['amount']),
                    'date': date_str,
                    'transaction_type': transaction_data.get('transaction_type', 'debit'),
                    'category': transaction_data.get('category', 'Others'),
                    'success': True,
                    'raw_text': request.sms_text,
                    'confidence': confidence_score
                }
                
                db_transaction = db_manager.add_transaction(db_transaction_data)
                
                # Add to deduplicator for future duplicate detection
                transaction_deduplicator.add_transaction(duplicate_check_data)
                
                # Convert to response model
                transaction_response = TransactionResponse(
                    vendor=db_transaction.vendor,
                    amount=db_transaction.amount,
                    date=db_transaction.date.isoformat(),
                    transaction_type=db_transaction.transaction_type,
                    category=db_transaction.category,
                    success=db_transaction.success,
                    raw_text=db_transaction.raw_text,
                    confidence=db_transaction.confidence
                )
                
                return transaction_response
            else:
                # Fallback to regex parsing if Gemini fails
                print(f"Gemini parsing failed: {gemini_result.get('error')}, falling back to regex")
                # Check if it was rejected as promotional
                if gemini_result.get('is_promotional'):
                    raise ValueError(f"Promotional message rejected: {gemini_result.get('error')}")
        
        # Fallback: Use regex-based parsing
        # Enhanced regex patterns for multiple banks
        if any(bank in request.sms_text for bank in ["HDFC Bank:", "SBI:", "ICICI Bank:", "Canara Bank"]) and any(action in request.sms_text.lower() for action in ["debited", "credited"]):
            # Extract amount
            amount_match = re.search(r'Rs\.(\d+(?:,\d+)*(?:\.\d{2})?)', request.sms_text)
            if amount_match:
                amount = float(amount_match.group(1).replace(',', ''))
                
                # Extract vendor
                vendor_match = re.search(r'at\s+([A-Z][A-Z0-9\s&.-]+)(?:\.|\s|$)', request.sms_text)
                vendor = vendor_match.group(1).strip() if vendor_match else "Unknown"
                
                # Extract date with multiple patterns
                date_patterns = [
                    r'on\s+(\d{1,2}-\d{1,2}-\d{4})',  # on 15-09-2024
                    r'on\s+(\d{1,2}/\d{1,2}/\d{4})',  # on 15/09/2024
                    r'on\s+(\d{1,2}-\d{1,2}-\d{2})',  # on 15-09-24
                    r'(\d{1,2}-\d{1,2}-\d{4})',       # 15-09-2024
                    r'(\d{1,2}/\d{1,2}/\d{4})',       # 15/09/2024
                    r'(\d{1,2}-\d{1,2}-\d{2})',       # 15-09-24
                ]
                
                date_str = None
                for pattern in date_patterns:
                    date_match = re.search(pattern, request.sms_text)
                    if date_match:
                        date_str = date_match.group(1)
                        break
                
                if not date_str:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                else:
                    # Format date properly
                    try:
                        # Handle different date formats
                        if len(date_str.split('-')[-1]) == 2 or len(date_str.split('/')[-1]) == 2:  # 2-digit year
                            if '-' in date_str:
                                parsed_date = datetime.strptime(date_str, '%d-%m-%y')
                            else:
                                parsed_date = datetime.strptime(date_str, '%d/%m/%y')
                            # Fix 2-digit year interpretation for banking transactions
                            # Ensure years are in reasonable range (2020-2030)
                            if parsed_date.year > 2030:
                                parsed_date = parsed_date.replace(year=parsed_date.year - 100)
                            elif parsed_date.year < 2020:
                                parsed_date = parsed_date.replace(year=parsed_date.year + 100)
                        else:  # 4-digit year
                            if '-' in date_str:
                                parsed_date = datetime.strptime(date_str, '%d-%m-%Y')
                            else:
                                parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
                        
                        # Validate date is reasonable
                        current_date = datetime.now()
                        if parsed_date > current_date:
                            date_str = current_date.strftime('%Y-%m-%d')
                        elif parsed_date < datetime(2020, 1, 1):
                            date_str = current_date.strftime('%Y-%m-%d')
                        else:
                            date_str = parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                
                # Determine transaction type
                transaction_type = 'credit' if 'credited' in request.sms_text.lower() else 'debit'
                
                # Create transaction data
                transaction_data = {
                    'vendor': vendor,
                    'amount': amount,
                    'date': date_str,
                    'transaction_type': transaction_type,
                    'category': 'Shopping' if 'AMAZON' in vendor else 'Others',
                    'success': True,
                    'raw_text': request.sms_text,
                    'confidence': 0.8  # Lower confidence for regex parsing
                }
                
                db_transaction = db_manager.add_transaction(transaction_data)
                
                # Convert to response model
                transaction_response = TransactionResponse(
                    vendor=db_transaction.vendor,
                    amount=db_transaction.amount,
                    date=db_transaction.date.isoformat(),
                    transaction_type=db_transaction.transaction_type,
                    category=db_transaction.category,
                    success=db_transaction.success,
                    raw_text=db_transaction.raw_text,
                    confidence=db_transaction.confidence
                )
                
                return transaction_response
            else:
                raise ValueError("Could not extract amount from HDFC Bank SMS")
        else:
            # Use the regular parser for other SMS formats
            parsed_transaction = sms_parser.parse_sms(request.sms_text)
            
            if parsed_transaction['success']:
                # Store in database with proper date handling
                transaction_data = {
                    'vendor': parsed_transaction['vendor'],
                    'amount': parsed_transaction['amount'],
                    'date': parsed_transaction['date'],
                    'transaction_type': parsed_transaction['transaction_type'],
                    'category': parsed_transaction['category'],
                    'success': parsed_transaction['success'],
                    'raw_text': parsed_transaction['raw_text'],
                    'confidence': parsed_transaction['confidence']
                }
                
                db_transaction = db_manager.add_transaction(transaction_data)
                
                # Convert to response model
                transaction_response = TransactionResponse(
                    vendor=db_transaction.vendor,
                    amount=db_transaction.amount,
                    date=db_transaction.date.isoformat(),
                    transaction_type=db_transaction.transaction_type,
                    category=db_transaction.category,
                    success=db_transaction.success,
                    raw_text=db_transaction.raw_text,
                    confidence=db_transaction.confidence
                )
                
                return transaction_response
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not parse transaction data from SMS"
                )
    except ValueError as e:
        print(f"ValueError in SMS parsing: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in SMS parsing: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/transactions", response_model=List[TransactionResponse])
async def get_transactions(limit: int = 100, offset: int = 0):
    """
    Retrieve all stored transactions with pagination
    """
    try:
        db_transactions = db_manager.get_transactions(limit=limit, offset=offset)
        
        transactions = []
        for db_transaction in db_transactions:
            transaction_response = TransactionResponse(
                vendor=db_transaction.vendor,
                amount=db_transaction.amount,
                date=db_transaction.date.isoformat(),
                transaction_type=db_transaction.transaction_type,
                category=db_transaction.category,
                success=db_transaction.success,
                raw_text=db_transaction.raw_text,
                confidence=db_transaction.confidence
            )
            transactions.append(transaction_response)
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    """
    Get a specific transaction by ID
    """
    try:
        db_transaction = db_manager.get_transaction_by_id(transaction_id)
        if not db_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return TransactionResponse(
            vendor=db_transaction.vendor,
            amount=db_transaction.amount,
            date=db_transaction.date.isoformat(),
            transaction_type=db_transaction.transaction_type,
            category=db_transaction.category,
            success=db_transaction.success,
            raw_text=db_transaction.raw_text,
            confidence=db_transaction.confidence
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/v1/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """
    Delete a transaction
    """
    try:
        success = db_manager.delete_transaction(transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/stats")
async def get_transaction_stats():
    """
    Get transaction statistics and analytics
    """
    try:
        stats = db_manager.get_transaction_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/categories")
async def get_categories():
    """
    Get all expense categories
    """
    try:
        categories = db_manager.get_categories()
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "color": cat.color,
                "icon": cat.icon
            }
            for cat in categories
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/search")
async def search_transactions(q: str, limit: int = 50):
    """
    Search transactions by vendor or category
    """
    try:
        db_transactions = db_manager.search_transactions(q, limit)
        
        transactions = []
        for db_transaction in db_transactions:
            transaction_response = TransactionResponse(
                vendor=db_transaction.vendor,
                amount=db_transaction.amount,
                date=db_transaction.date.isoformat(),
                transaction_type=db_transaction.transaction_type,
                category=db_transaction.category,
                success=db_transaction.success,
                raw_text=db_transaction.raw_text,
                confidence=db_transaction.confidence
            )
            transactions.append(transaction_response)
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/transactions", response_model=TransactionResponse)
async def add_transaction(transaction: TransactionResponse):
    """
    Add a new transaction directly
    """
    try:
        # Convert to database format
        transaction_data = {
            'vendor': transaction.vendor,
            'amount': transaction.amount,
            'date': datetime.fromisoformat(transaction.date),
            'transaction_type': transaction.transaction_type,
            'category': transaction.category,
            'success': transaction.success,
            'raw_text': transaction.raw_text,
            'confidence': transaction.confidence
        }
        
        db_transaction = db_manager.add_transaction(transaction_data)
        
        # Convert to response model
        transaction_response = TransactionResponse(
            vendor=db_transaction.vendor,
            amount=db_transaction.amount,
            date=db_transaction.date.isoformat(),
            transaction_type=db_transaction.transaction_type,
            category=db_transaction.category,
            success=db_transaction.success,
            raw_text=db_transaction.raw_text,
            confidence=db_transaction.confidence
        )
        
        return transaction_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/categorize")
async def categorize_vendor(vendor: str):
    """
    Categorize a vendor using ML model
    """
    try:
        category, confidence = ml_categorizer.predict_category(vendor)
        probabilities = ml_categorizer.get_category_probabilities(vendor)
        
        return {
            "vendor": vendor,
            "predicted_category": category,
            "confidence": confidence,
            "all_probabilities": probabilities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/ml-info")
async def get_ml_model_info():
    """
    Get information about the ML categorization model
    """
    try:
        info = ml_categorizer.get_model_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/analytics/spending-by-category")
async def get_spending_by_category():
    """
    Get spending breakdown by category with robust analytics
    """
    try:
        return robust_analytics.get_spending_by_category()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/analytics/monthly-trends")
async def get_monthly_trends():
    """
    Get monthly spending trends with robust analytics
    """
    try:
        return robust_analytics.get_monthly_trends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/analytics/insights")
async def get_spending_insights():
    """
    Get spending insights with robust analytics
    """
    try:
        return robust_analytics.get_spending_insights()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/analytics/top-vendors")
async def get_top_vendors(limit: int = 10):
    """
    Get top vendors with robust analytics
    """
    try:
        return robust_analytics.get_top_vendors(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Monthly Tracking Endpoints
@app.get("/v1/monthly/summary")
async def get_monthly_summary(year: int = None, month: int = None):
    """
    Get comprehensive monthly summary
    """
    try:
        return monthly_tracker.get_monthly_summary(year, month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/monthly/yearly-overview")
async def get_yearly_overview(year: int = None):
    """
    Get yearly overview with monthly breakdowns
    """
    try:
        return monthly_tracker.get_yearly_overview(year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/monthly/trends")
async def get_monthly_trends(months: int = 6):
    """
    Get spending trends over the last N months
    """
    try:
        return monthly_tracker.get_spending_trends(months)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Gemini AI Endpoints
class AIAnalysisRequest(BaseModel):
    transaction_limit: int = 100

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

@app.post("/v1/ai/analyze-spending")
async def ai_analyze_spending(request: AIAnalysisRequest):
    """
    Get AI-powered spending analysis using Gemini
    """
    try:
        if not gemini_assistant:
            raise HTTPException(status_code=503, detail="AI assistant not available")
        
        # Get recent transactions
        transactions = db_manager.get_transactions(limit=request.transaction_limit)
        transaction_data = [
            {
                'vendor': t.vendor,
                'amount': t.amount,
                'date': t.date.isoformat(),
                'transaction_type': t.transaction_type,
                'category': t.category
            }
            for t in transactions
        ]
        
        analysis = gemini_assistant.analyze_spending_patterns(transaction_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/ai/financial-advice")
async def get_financial_advice():
    """
    Get personalized financial advice from AI
    """
    try:
        if not gemini_assistant:
            raise HTTPException(status_code=503, detail="AI assistant not available")
        
        # Get user's financial context
        stats = db_manager.get_transaction_stats()
        context = {
            'total_income': stats.get('total_received', 0),
            'total_spending': stats.get('total_spent', 0),
            'net_balance': stats.get('net_balance', 0),
            'top_categories': list(stats.get('category_breakdown', {}).keys())[:3]
        }
        
        advice = gemini_assistant.generate_financial_advice(context)
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/ai/chat")
async def chat_with_ai(request: ChatRequest):
    """
    Chat with AI financial assistant
    """
    try:
        if not gemini_assistant:
            raise HTTPException(status_code=503, detail="AI assistant not available")
        
        response = gemini_assistant.chat_with_assistant(request.message, request.context)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/ai/monthly-report")
async def get_ai_monthly_report(year: int = None, month: int = None):
    """
    Get AI-generated monthly financial report
    """
    try:
        if not gemini_assistant:
            raise HTTPException(status_code=503, detail="AI assistant not available")
        
        # Get monthly data
        monthly_summary = monthly_tracker.get_monthly_summary(year, month)
        if not monthly_summary['success']:
            raise HTTPException(status_code=404, detail="Monthly data not found")
        
        report = gemini_assistant.generate_monthly_report(monthly_summary['data'])
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Predictive Analytics Endpoints
@app.post("/v1/predictions/train-models")
async def train_prediction_models(db: Session = Depends(get_db)):
    """
    Train predictive models using historical transaction data
    """
    try:
        # Get all transactions for training
        transactions = db_manager.get_all_transactions(db)
        transactions_data = [
            {
                'vendor': t.vendor,
                'amount': t.amount,
                'date': t.date,
                'transaction_type': t.transaction_type,
                'category': t.category,
                'success': t.success
            }
            for t in transactions
        ]
        
        # Train models
        model_scores = predictive_engine.train_spending_models(transactions_data)
        
        return {
            "message": "Models trained successfully",
            "categories_trained": list(model_scores.keys()),
            "model_scores": model_scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/predictions/spending-forecast")
async def get_spending_forecast(category: str = None, db: Session = Depends(get_db)):
    """
    Get spending predictions for categories
    """
    try:
        if category:
            # Predict for specific category
            forecast = predictive_engine.predict_spending(category)
            if forecast:
                return {
                    "category": forecast.category,
                    "current_month_prediction": forecast.current_month_prediction,
                    "next_month_prediction": forecast.next_month_prediction,
                    "confidence_score": forecast.confidence_score,
                    "trend": forecast.trend,
                    "recommendation": forecast.recommendation
                }
            else:
                raise HTTPException(status_code=404, detail=f"No model available for category: {category}")
        else:
            # Predict for all available categories
            forecasts = []
            for cat in predictive_engine.models.keys():
                forecast = predictive_engine.predict_spending(cat)
                if forecast:
                    forecasts.append({
                        "category": forecast.category,
                        "current_month_prediction": forecast.current_month_prediction,
                        "next_month_prediction": forecast.next_month_prediction,
                        "confidence_score": forecast.confidence_score,
                        "trend": forecast.trend,
                        "recommendation": forecast.recommendation
                    })
            
            return {"forecasts": forecasts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SavingsGoalRequest(BaseModel):
    target_amount: float
    target_months: int
    current_income: float
    current_expenses: float

@app.post("/v1/predictions/savings-goal")
async def create_savings_goal(goal_request: SavingsGoalRequest):
    """
    Create and analyze a savings goal
    """
    try:
        savings_goal = predictive_engine.create_savings_goal(
            target_amount=goal_request.target_amount,
            target_months=goal_request.target_months,
            current_income=goal_request.current_income,
            current_expenses=goal_request.current_expenses
        )
        
        return {
            "goal_id": savings_goal.goal_id,
            "target_amount": savings_goal.target_amount,
            "current_saved": savings_goal.current_saved,
            "target_date": savings_goal.target_date.isoformat(),
            "monthly_required": savings_goal.monthly_required,
            "achievable": savings_goal.achievable,
            "recommendation": savings_goal.recommendation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class BudgetLimits(BaseModel):
    limits: dict  # category -> limit amount

@app.post("/v1/predictions/budget-alerts")
async def get_budget_alerts(budget_limits: BudgetLimits, db: Session = Depends(get_db)):
    """
    Get budget alerts based on current spending vs limits
    """
    try:
        # Get current month spending by category
        category_spending = db_manager.get_spending_by_category(db)
        current_spending = {category: amount for category, amount in category_spending}
        
        # Generate alerts
        alerts = predictive_engine.generate_budget_alerts(current_spending, budget_limits.limits)
        
        return {
            "alerts": [
                {
                    "category": alert.category,
                    "current_spending": alert.current_spending,
                    "budget_limit": alert.budget_limit,
                    "percentage_used": alert.percentage_used,
                    "alert_level": alert.alert_level,
                    "message": alert.message
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/predictions/financial-insights")
async def get_financial_insights(db: Session = Depends(get_db)):
    """
    Get personalized financial insights and recommendations
    """
    try:
        # Get all transactions for analysis
        transactions = db_manager.get_all_transactions(db)
        transactions_data = [
            {
                'vendor': t.vendor,
                'amount': t.amount,
                'date': t.date,
                'transaction_type': t.transaction_type,
                'category': t.category,
                'success': t.success
            }
            for t in transactions
        ]
        
        # Generate insights
        insights = predictive_engine.get_financial_insights(transactions_data)
        
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Group Expenses Endpoints
class GroupCreateRequest(BaseModel):
    name: str
    description: str = ""
    created_by: str

class GroupMemberRequest(BaseModel):
    user_identifier: str
    name: str

class GroupExpenseRequest(BaseModel):
    paid_by: str
    amount: float
    description: str
    category: str = "Other"
    split_method: str = "equal"
    split_data: dict = None

@app.post("/v1/groups")
async def create_group(request: GroupCreateRequest, db: Session = Depends(get_db)):
    """Create a new expense group"""
    try:
        group = group_expense_manager.create_group(
            db, request.name, request.description, request.created_by
        )
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_by": group.created_by,
            "created_at": group.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/groups/{group_id}/members")
async def add_group_member(group_id: int, request: GroupMemberRequest, db: Session = Depends(get_db)):
    """Add a member to a group"""
    try:
        member = group_expense_manager.add_member(
            db, group_id, request.user_identifier, request.name
        )
        return {
            "id": member.id,
            "user_identifier": member.user_identifier,
            "name": member.name,
            "joined_at": member.joined_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/groups/{group_id}/expenses")
async def add_group_expense(group_id: int, request: GroupExpenseRequest, db: Session = Depends(get_db)):
    """Add an expense to a group"""
    try:
        expense = group_expense_manager.add_expense(
            db, group_id, request.paid_by, request.amount,
            request.description, request.category,
            request.split_method, request.split_data
        )
        return {
            "id": expense.id,
            "amount": expense.amount,
            "description": expense.description,
            "paid_by": expense.paid_by,
            "category": expense.category,
            "date": expense.date.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/groups/{group_id}/summary")
async def get_group_summary(group_id: int, db: Session = Depends(get_db)):
    """Get comprehensive group summary"""
    try:
        return group_expense_manager.get_group_summary(db, group_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/users/{user_identifier}/groups")
async def get_user_groups(user_identifier: str, db: Session = Depends(get_db)):
    """Get all groups for a user"""
    try:
        groups = group_expense_manager.get_user_groups(db, user_identifier)
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/users/{user_identifier}/settlements")
async def get_pending_settlements(user_identifier: str, db: Session = Depends(get_db)):
    """Get pending settlements for a user"""
    try:
        settlements = group_expense_manager.get_pending_settlements(db, user_identifier)
        return {"settlements": settlements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
