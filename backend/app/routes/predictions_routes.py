"""Predictions routes: savings goal and simple predictive helpers"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, conint, confloat
from datetime import datetime
from sqlalchemy.orm import Session
from predictive_analytics import PredictiveAnalytics
from app.config.database import get_db
from app.models.transaction import Transaction

router = APIRouter(prefix="/v1/predictions", tags=["predictions"])

class SavingsGoalRequest(BaseModel):
    target_amount: confloat(gt=0) = Field(..., description="Target savings amount in INR")
    target_months: conint(gt=0) = Field(..., description="Months to reach the goal")
    current_income: confloat(ge=0) = Field(..., description="Monthly income")
    current_expenses: confloat(ge=0) = Field(..., description="Monthly expenses")

class SavingsGoalResponse(BaseModel):
    goal_id: str
    target_amount: float
    current_saved: float
    target_date: str
    monthly_required: float
    achievable: bool
    recommendation: str

@router.post("/savings-goal", response_model=SavingsGoalResponse)
async def create_savings_goal(req: SavingsGoalRequest):
    """Compute a savings plan suggestion. Public, stateless."""
    try:
        engine = PredictiveAnalytics()
        goal = engine.create_savings_goal(
            target_amount=req.target_amount,
            target_months=req.target_months,
            current_income=req.current_income,
            current_expenses=req.current_expenses,
        )
        # Serialize dataclass to response
        return SavingsGoalResponse(
            goal_id=goal.goal_id,
            target_amount=goal.target_amount,
            current_saved=goal.current_saved,
            target_date=goal.target_date.strftime("%Y-%m-%d"),
            monthly_required=goal.monthly_required,
            achievable=goal.achievable,
            recommendation=goal.recommendation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute savings goal: {str(e)}")

class TrainModelsResponse(BaseModel):
    categories_trained: list[str] = []
    message: str

@router.post("/train-models", response_model=TrainModelsResponse)
async def train_models(db: Session = Depends(get_db)):
    """Train per-category spending models from existing transactions (debits only)."""
    try:
        # Pull recent transactions (limit to last 6 months for speed)
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=180)
        txs = db.query(Transaction).filter(Transaction.date.isnot(None)).all()
        # Fallback to created_at when date is None
        if not txs:
            txs = db.query(Transaction).all()

        data = []
        for t in txs:
            d = t.date or t.created_at
            if d is None:
                continue
            if (datetime.now() - d).days > 180:
                continue
            data.append({
                'category': t.category or 'Others',
                'amount': float(t.amount or 0.0),
                'date': d.strftime('%Y-%m-%d'),
                'transaction_type': (t.transaction_type or 'debit')
            })

        engine = PredictiveAnalytics()
        scores = engine.train_spending_models(data)
        cats = sorted(list(scores.keys()))
        return TrainModelsResponse(
            categories_trained=cats,
            message=f"Trained {len(cats)} categories"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train models: {str(e)}")
