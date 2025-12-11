"""
Enhanced Chatbot Routes - Improved with intelligent transaction context
Uses parsed transactions as knowledge base and integrates with query cache
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.config.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.transaction import Transaction
from app.utils.intelligent_query_cache import IntelligentQueryCache
from app.utils.ollama_integration import OllamaAssistant
from datetime import datetime, timedelta

router = APIRouter(prefix="/v1/enhanced-chatbot", tags=["enhanced-chatbot"])

# Global instances
query_cache = IntelligentQueryCache()
ollama_assistant = OllamaAssistant()

# Simple in-memory session context (per user) for 15 minutes
SESSION_CONTEXT: Dict[int, Dict[str, Any]] = {}
SESSION_TTL_SECONDS = 900

class EnhancedChatQuery(BaseModel):
    query: str
    use_cache: bool = True
    include_context: bool = True
    refresh_session: bool = False

class EnhancedChatResponse(BaseModel):
    response: str
    transaction_count: int
    query: str
    cached: bool
    processing_time: float
    context_used: bool
    data_quality: Dict[str, Any]

@router.post("/ask", response_model=EnhancedChatResponse)
async def enhanced_chatbot_query(
    request: EnhancedChatQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enhanced chatbot that uses your parsed transactions as intelligent context"""
    
    start_time = datetime.now()
    
    try:
        # Build or reuse session context: last 30 days up to 100 transactions
        cutoff = datetime.now() - timedelta(days=30)
        need_refresh = request.refresh_session or (current_user.id not in SESSION_CONTEXT) or (
            SESSION_CONTEXT.get(current_user.id, {}).get("expires_at") is None or
            SESSION_CONTEXT[current_user.id]["expires_at"] < datetime.now()
        )

        if need_refresh:
            transactions = db.query(Transaction).filter(
                Transaction.user_id == current_user.id,
                or_(
                    and_(Transaction.date.isnot(None), Transaction.date >= cutoff),
                    and_(Transaction.date.is_(None), Transaction.created_at >= cutoff)
                )
            ).order_by(Transaction.created_at.desc()).limit(100).all()

            if not transactions:
                return EnhancedChatResponse(
                    response="I don't see transactions from the last month. Once you process some SMS messages, I'll be able to provide insights!",
                    transaction_count=0,
                    query=request.query,
                    cached=False,
                    processing_time=0.0,
                    context_used=False,
                    data_quality={"status": "no_data"}
                )

            # Build rich context once per session and cache it
            context_str = _prepare_rich_transaction_context(transactions)
            SESSION_CONTEXT[current_user.id] = {
                "context": context_str,
                "count": len(transactions),
                "built_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=SESSION_TTL_SECONDS)
            }
        else:
            transactions = []  # Not needed when reusing context
            context_str = SESSION_CONTEXT[current_user.id]["context"]

        # Analyze data quality (when we have transactions freshly loaded)
        data_quality = _analyze_data_quality(transactions) if transactions else {"status": "cached_context"}

        # Try cached response first if enabled
        if request.use_cache:
            try:
                cached_result = await query_cache.get_cached_response(
                    request.query, current_user.id, db
                )
                
                if cached_result["cached"]:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    return EnhancedChatResponse(
                        response=cached_result["response"],
                        transaction_count=len(transactions),
                        query=request.query,
                        cached=True,
                        processing_time=processing_time,
                        context_used=True,
                        data_quality=data_quality
                    )
            except Exception as e:
                print(f"Cache error: {e}")
        
        # Generate new response with enhanced context
        if request.include_context:
            enhanced_response = await _generate_enhanced_response_with_context(
                request.query, context_str, current_user.id
            )
        else:
            # Fallback to simple analytics if no context requested
            # Recompute minimal transactions for fallback if needed
            if not transactions:
                transactions = db.query(Transaction).filter(
                    Transaction.user_id == current_user.id
                ).order_by(Transaction.created_at.desc()).limit(30).all()
            enhanced_response = await _generate_simple_response(
                request.query, transactions
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return EnhancedChatResponse(
            response=enhanced_response,
            transaction_count=SESSION_CONTEXT.get(current_user.id, {}).get("count", len(transactions)),
            query=request.query,
            cached=False,
            processing_time=processing_time,
            context_used=request.include_context,
            data_quality=data_quality
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return EnhancedChatResponse(
            response=f"I encountered an error while analyzing your transactions: {str(e)}. Please try a different question.",
            transaction_count=0,
            query=request.query,
            cached=False,
            processing_time=processing_time,
            context_used=False,
            data_quality={"status": "error", "error": str(e)}
        )

async def _generate_enhanced_response(query: str, transactions: List[Transaction], user_id: int) -> str:
    """Generate enhanced response using transaction context and LLM"""
    context = _prepare_rich_transaction_context(transactions)
    return await _generate_enhanced_response_with_context(query, context, user_id)

async def _generate_enhanced_response_with_context(query: str, context: str, user_id: int) -> str:
    """Generate enhanced response using a prebuilt context string and LLM"""
    # Create enhanced prompt
    prompt = f"""
You are a financial advisor analyzing a user's transaction data. Provide helpful, specific insights based on the data.

TRANSACTION DATA SUMMARY:
{context}

USER QUESTION: {query}

Instructions:
- Use the actual transaction data to provide specific, accurate answers
- Include relevant numbers, percentages, and insights
- Be conversational and helpful
- If asking about spending, focus on debit transactions (money going out)
- If asking about income, focus on credit transactions (money coming in)
- Suggest actionable financial advice when appropriate
- Keep response under 200 words but be informative

Answer:
"""
    
    try:
        # Use the enhanced LLM integration
        result = await ollama_assistant.generate_response(prompt)
        
        if result.get('success', False):
            return result['response']
        else:
            return f"I can see you have {len(transactions)} transactions. {result.get('response', 'Please try asking about your spending categories, amounts, or trends.')}"
            
    except Exception as e:
        # Fallback to analytical response
        return _generate_analytical_fallback(query, transactions)

def _prepare_rich_transaction_context(transactions: List[Transaction]) -> str:
    """Prepare rich context from transactions for LLM"""
    
    if not transactions:
        return "No transaction data available."
    
    # Analyze transactions
    total_amount = sum(tx.amount for tx in transactions if tx.amount)
    transaction_count = len(transactions)
    
    # Category analysis
    categories = {}
    vendors = {}
    monthly_spending = {}
    
    for tx in transactions:
        if not tx.amount:
            continue
            
        # Category breakdown
        category = tx.category or "Others"
        categories[category] = categories.get(category, 0) + tx.amount
        
        # Vendor breakdown  
        vendor = tx.vendor or "Unknown"
        vendors[vendor] = vendors.get(vendor, 0) + tx.amount
        
        # Monthly breakdown
        try:
            if tx.date:
                if isinstance(tx.date, str):
                    month_key = tx.date[:7]  # YYYY-MM
                else:
                    month_key = tx.date.strftime("%Y-%m")
            else:
                month_key = tx.created_at.strftime("%Y-%m")
            monthly_spending[month_key] = monthly_spending.get(month_key, 0) + tx.amount
        except:
            pass
    
    # Build context
    context = f"""
Total Transactions: {transaction_count}
Total Amount: Rs.{total_amount:,.2f}
Date Range: {transactions[-1].created_at.strftime('%Y-%m-%d')} to {transactions[0].created_at.strftime('%Y-%m-%d')}

TOP SPENDING CATEGORIES:
"""
    
    # Top categories
    sorted_categories = sorted(categories.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    for category, amount in sorted_categories:
        context += f"- {category}: Rs.{amount:,.2f}\n"
    
    context += "\nTOP VENDORS:\n"
    # Top vendors
    sorted_vendors = sorted(vendors.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
    for vendor, amount in sorted_vendors:
        context += f"- {vendor}: Rs.{amount:,.2f}\n"
    
    # Recent transactions
    context += "\nRECENT TRANSACTIONS:\n"
    for tx in transactions[:10]:
        date_str = tx.date or tx.created_at.strftime('%Y-%m-%d')
        context += f"- {date_str}: {tx.vendor or 'Unknown'} - Rs.{tx.amount:,.2f} ({tx.category or 'Others'})\n"
    
    return context

def _generate_analytical_fallback(query: str, transactions: List[Transaction]) -> str:
    """Generate analytical response without LLM"""
    
    query_lower = query.lower()
    
    # Calculate metrics
    total_amount = sum(tx.amount for tx in transactions if tx.amount)
    avg_amount = total_amount / len(transactions) if transactions else 0
    
    # Category analysis
    categories = {}
    vendors = {}
    for tx in transactions:
        if tx.amount:
            categories[tx.category or "Others"] = categories.get(tx.category or "Others", 0) + tx.amount
            vendors[tx.vendor or "Unknown"] = vendors.get(tx.vendor or "Unknown", 0) + tx.amount
    
    # Response based on query type
    if any(word in query_lower for word in ['spend', 'spent', 'total', 'much']):
        return f"Based on your {len(transactions)} transactions, your total spending is Rs.{total_amount:,.2f}. Your average transaction amount is Rs.{avg_amount:,.2f}."
    
    elif any(word in query_lower for word in ['category', 'categories']):
        top_categories = sorted(categories.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        response = "Your top spending categories are:\n"
        for i, (cat, amt) in enumerate(top_categories, 1):
            response += f"{i}. {cat}: Rs.{amt:,.2f}\n"
        return response
    
    elif any(word in query_lower for word in ['vendor', 'merchant', 'store']):
        top_vendors = sorted(vendors.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        response = "You spend the most at:\n"
        for i, (vendor, amt) in enumerate(top_vendors, 1):
            response += f"{i}. {vendor}: Rs.{amt:,.2f}\n"
        return response
    
    else:
        return f"I can analyze your {len(transactions)} transactions. You can ask me about spending totals, categories, vendors, or trends. For example: 'How much did I spend on subscriptions?' or 'What's my biggest expense category?'"

async def _generate_simple_response(query: str, transactions: List[Transaction]) -> str:
    """Generate simple response without heavy context"""
    return _generate_analytical_fallback(query, transactions)

def _analyze_data_quality(transactions: List[Transaction]) -> Dict[str, Any]:
    """Analyze the quality of transaction data"""
    
    if not transactions:
        return {"status": "no_data", "quality_score": 0}
    
    total_count = len(transactions)
    
    # Check data completeness
    with_amounts = sum(1 for tx in transactions if tx.amount and tx.amount != 0)
    with_vendors = sum(1 for tx in transactions if tx.vendor and tx.vendor.strip())
    with_categories = sum(1 for tx in transactions if tx.category and tx.category.strip())
    with_dates = sum(1 for tx in transactions if tx.date)
    
    # Calculate quality score
    completeness_score = (with_amounts + with_vendors + with_categories + with_dates) / (total_count * 4)
    quality_score = completeness_score * 100
    
    return {
        "status": "analyzed",
        "total_transactions": total_count,
        "quality_score": round(quality_score, 1),
        "completeness": {
            "amounts": f"{with_amounts}/{total_count}",
            "vendors": f"{with_vendors}/{total_count}",
            "categories": f"{with_categories}/{total_count}",
            "dates": f"{with_dates}/{total_count}"
        },
        "data_range": {
            "from": transactions[-1].created_at.strftime("%Y-%m-%d") if transactions else None,
            "to": transactions[0].created_at.strftime("%Y-%m-%d") if transactions else None
        }
    }

@router.get("/data-quality")
async def get_data_quality_report(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get data quality report for chatbot context"""
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    quality_report = _analyze_data_quality(transactions)
    
    return {
        "success": True,
        "user_id": current_user.id,
        "data_quality": quality_report,
        "recommendations": _get_quality_recommendations(quality_report)
    }

def _get_quality_recommendations(quality_report: Dict[str, Any]) -> List[str]:
    """Get recommendations based on data quality"""
    
    recommendations = []
    
    if quality_report.get("quality_score", 0) < 70:
        recommendations.append("Consider processing more SMS messages to improve data quality")
    
    if quality_report.get("total_transactions", 0) < 20:
        recommendations.append("More transaction data will help provide better insights")
    
    completeness = quality_report.get("completeness", {})
    
    if "0/" in completeness.get("vendors", ""):
        recommendations.append("Vendor information is missing - this affects spending analysis")
    
    if "0/" in completeness.get("categories", ""):
        recommendations.append("Category information is missing - this affects spending breakdowns")
    
    if not recommendations:
        recommendations.append("Your transaction data quality is good for generating insights!")
    
    return recommendations

@router.post("/conversation-history")
async def save_conversation(
    query: str,
    response: str,
    current_user: User = Depends(get_current_active_user)
):
    """Save conversation history for learning (future enhancement)"""
    
    # This could be enhanced to save conversation history
    # for improving responses over time
    
    return {
        "success": True,
        "message": "Conversation saved for future improvements",
        "user_id": current_user.id
    }
