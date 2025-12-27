"""
Chatbot API Routes
Provides endpoints for financial chatbot functionality
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.controllers import chatbot_controller
from app.config.database import get_db
from app.models.transaction import Transaction

router = APIRouter(prefix="/v1/chatbot", tags=["Financial Chatbot"])


class ChatbotQuery(BaseModel):
    query: str
    limit: Optional[int] = 100  # Limit number of transactions to analyze


class ChatbotResponse(BaseModel):
    response: str
    transaction_count: int
    query: str


@router.post("/query", response_model=ChatbotResponse)
async def query_chatbot(
    request: ChatbotQuery,
    db: Session = Depends(get_db)
):
    """
    Query the financial chatbot about your transactions.
    The chatbot will analyze your transaction history and provide intelligent responses.
    """
    try:
        print(f"🤖 Chatbot query received: {request.query}")
        
        # Fetch transactions from database (using public endpoint approach)
        transactions = db.query(Transaction).order_by(Transaction.date.desc()).limit(request.limit).all()
        
        print(f"📊 Found {len(transactions)} transactions")
        
        if not transactions:
            return ChatbotResponse(
                response="I don't see any transactions in your account yet. Once you start adding transactions, I'll be able to help you analyze your spending patterns and provide financial insights!",
                transaction_count=0,
                query=request.query
            )
        
        # Get the chatbot's response (limit transactions for faster processing)
        limited_transactions = transactions[:30]  # Limit to 30 most recent transactions
        print(f"🤖 Processing query with {len(limited_transactions)} transactions")
        response_data = await chatbot_controller.get_chatbot_response(request.query, limited_transactions)
        
        print(f"✅ Chatbot response generated successfully")
        return ChatbotResponse(**response_data)
        
    except Exception as e:
        error_msg = f"Chatbot service error: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/summary")
async def get_financial_summary(
    db: Session = Depends(get_db),
    days: int = Query(30, description="Number of days to analyze")
):
    """
    Get a financial summary for the chatbot context.
    """
    try:
        # Get recent transactions
        transactions = db.query(Transaction).order_by(Transaction.date.desc()).limit(days * 5).all()  # Approximate
        
        summary = await chatbot_controller.get_spending_summary(transactions)
        
        return {
            "summary": summary,
            "period_days": days,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")


@router.post("/quick-insights")
async def get_quick_insights(
    db: Session = Depends(get_db)
):
    """
    Get quick financial insights without a specific query.
    """
    try:
        # Get recent transactions
        transactions = db.query(Transaction).order_by(Transaction.date.desc()).limit(50).all()
        
        if not transactions:
            return {
                "insights": ["No transactions found. Start adding transactions to get personalized insights!"],
                "transaction_count": 0
            }
        
        # Generate automatic insights with a simpler, faster query
        insights_query = "Give me 3 quick insights about my spending in 2-3 sentences each."
        
        # Limit transactions for faster processing
        limited_transactions = transactions[:20]  # Only use last 20 transactions
        response_data = await chatbot_controller.get_chatbot_response(insights_query, limited_transactions)
        
        return {
            "insights": response_data["response"],
            "transaction_count": response_data["transaction_count"],
            "auto_generated": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation error: {str(e)}")


# Public endpoints (no authentication required)
# Public chatbot endpoints removed - all endpoints now require authentication
