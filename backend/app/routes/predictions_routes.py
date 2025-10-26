"""Predictions routes: savings goal and simple predictive helpers"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, conint, confloat
from datetime import datetime
from predictive_analytics import PredictiveAnalytics

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