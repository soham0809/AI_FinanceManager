"""
Chatbot Controller for Financial Transaction Queries
Provides intelligent responses to user queries about their transaction data
"""
import json
import requests
from typing import List, Dict, Any
from app.models.transaction import Transaction
from app.config.settings import settings


def format_transactions_for_prompt(transactions: List[Transaction]) -> str:
    """Formats a list of transaction objects into a string for the LLM prompt."""
    if not transactions:
        return "No transactions found."
    
    transaction_lines = []
    for t in transactions:
        # Format transaction data for the AI
        # Use transaction_type from model
        transaction_type = t.transaction_type if t.transaction_type else "debit"
        transaction_lines.append(
            f"- Date: {t.date}, "
            f"Vendor: {t.vendor}, "
            f"Amount: ₹{t.amount:.2f}, "
            f"Type: {transaction_type}, "
            f"Category: {t.category}"
        )
    
    return "\n".join(transaction_lines)


async def get_ollama_response(prompt: str) -> str:
    """Get response from Ollama AI"""
    try:
        print(f"🤖 Sending request to Ollama at {settings.OLLAMA_HOST}")
        
        payload = {
            "model": "mistral:7b-instruct-q4_K_M",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=120  # Increased timeout
        )
        
        print(f"🤖 Ollama response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data.get('response', 'Sorry, I could not process your request.')
            print(f"🤖 AI Response length: {len(ai_response)} characters")
            return ai_response
        else:
            error_msg = f"Ollama API returned status {response.status_code}"
            print(f"❌ {error_msg}")
            return f"Sorry, I'm having trouble connecting to the AI service. (Status: {response.status_code})"
            
    except requests.exceptions.Timeout:
        error_msg = "Ollama request timed out"
        print(f"❌ {error_msg}")
        return "Sorry, the AI is taking too long to respond. Please try a simpler question."
    except requests.exceptions.ConnectionError:
        error_msg = "Cannot connect to Ollama service"
        print(f"❌ {error_msg}")
        return "Sorry, I can't connect to the AI service. Please make sure Ollama is running."
    except Exception as e:
        error_msg = f"Ollama request error: {e}"
        print(f"❌ {error_msg}")
        return f"Sorry, I encountered an error: {str(e)}"


async def get_chatbot_response(query: str, transactions: List[Transaction]) -> Dict[str, Any]:
    """
    Generates a response to a user's query based on their transaction history.
    """
    # First try to answer with simple analytics
    simple_response = generate_simple_response(query, transactions)
    if simple_response:
        return {
            "response": simple_response,
            "transaction_count": len(transactions),
            "query": query,
            "source": "analytics",  # Indicates response from built-in analytics
            "source_description": "Built-in Analytics"
        }
    
    # If simple response doesn't work, try AI (with timeout protection)
    try:
        formatted_transactions = format_transactions_for_prompt(transactions[:10])  # Limit to 10 transactions
        
        # Create a very concise prompt
        prompt = f"""
Answer briefly: {query}

Data: {formatted_transactions}

Keep under 100 words. Use ₹ for currency.
"""
        
        # Get the response from the local LLM with shorter timeout
        response = await get_ollama_response_fast(prompt)
        
        return {
            "response": response,
            "transaction_count": len(transactions),
            "query": query,
            "source": "ai_model",  # Indicates response from AI model
            "source_description": "Ollama AI (mistral:7b-instruct-q4_K_M)"
        }
    except:
        # Fallback to simple response
        return {
            "response": f"I found {len(transactions)} transactions in your account. You can ask me about spending patterns, categories, or specific vendors. For example: 'How much did I spend on food?' or 'What's my biggest expense?'",
            "transaction_count": len(transactions),
            "query": query,
            "source": "fallback",  # Indicates fallback response
            "source_description": "Default Response"
        }


def generate_simple_response(query: str, transactions: List[Transaction]) -> str:
    """Generate simple responses without AI for common queries"""
    query_lower = query.lower()
    
    if not transactions:
        return "I don't see any transactions yet. Once you add some transactions, I'll be able to help analyze your spending!"
    
    # Calculate basic stats using transaction_type
    total_spent = sum(t.amount for t in transactions if t.transaction_type == 'debit')
    total_earned = sum(t.amount for t in transactions if t.transaction_type == 'credit')
    
    # Category breakdown
    categories = {}
    vendors = {}
    for t in transactions:
        if t.transaction_type == 'debit':  # Debit transactions
            categories[t.category] = categories.get(t.category, 0) + t.amount
            vendors[t.vendor] = vendors.get(t.vendor, 0) + t.amount
    
    # Common query patterns
    if any(word in query_lower for word in ['spend', 'spent', 'total', 'much']):
        if 'month' in query_lower:
            return f"Based on your recent transactions, you've spent ₹{total_spent:.2f} and earned ₹{total_earned:.2f}. Your net spending is ₹{total_spent - total_earned:.2f}."
        else:
            return f"You've spent ₹{total_spent:.2f} across {len([t for t in transactions if t.transaction_type == 'debit'])} transactions."
    
    if any(word in query_lower for word in ['category', 'categories', 'breakdown']):
        if categories:
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
            response = "Your top spending categories are: "
            response += ", ".join([f"{cat}: ₹{amt:.2f}" for cat, amt in top_categories])
            return response
    
    if any(word in query_lower for word in ['vendor', 'merchant', 'shop', 'store']):
        if vendors:
            top_vendors = sorted(vendors.items(), key=lambda x: x[1], reverse=True)[:3]
            response = "You spend the most at: "
            response += ", ".join([f"{vendor}: ₹{amt:.2f}" for vendor, amt in top_vendors])
            return response
    
    if 'average' in query_lower:
        if transactions:
            debit_transactions = [t for t in transactions if t.transaction_type == 'debit']
            if debit_transactions:
                avg_amount = total_spent / len(debit_transactions)
                return f"Your average transaction amount is ₹{avg_amount:.2f}."
    
    return None  # Let AI handle complex queries


async def get_ollama_response_fast(prompt: str) -> str:
    """Get response from Ollama AI with shorter timeout"""
    try:
        print(f"🤖 Sending fast request to Ollama")
        
        payload = {
            "model": "mistral:7b-instruct-q4_K_M",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=30  # Shorter timeout
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('response', 'I can help you analyze your transactions. Try asking about spending categories or amounts.')
        else:
            return "I can help you analyze your transactions. Try asking about spending categories or amounts."
            
    except Exception as e:
        print(f"❌ Fast Ollama error: {e}")
        return "I can help you analyze your transactions. Try asking about spending categories or amounts."


async def get_spending_summary(transactions: List[Transaction]) -> Dict[str, Any]:
    """Generate a spending summary for the chatbot context"""
    if not transactions:
        return {"total_spent": 0, "categories": {}, "recent_count": 0}
    
    # Calculate basic statistics using transaction_type
    total_spent = sum(t.amount for t in transactions if t.transaction_type == 'debit')
    total_earned = sum(t.amount for t in transactions if t.transaction_type == 'credit')
    
    # Category breakdown
    categories = {}
    for t in transactions:
        if t.transaction_type == 'debit':  # Only count expenses
            if t.category in categories:
                categories[t.category] += t.amount
            else:
                categories[t.category] = t.amount
    
    return {
        "total_spent": total_spent,
        "total_earned": total_earned,
        "categories": categories,
        "transaction_count": len(transactions),
        "top_category": max(categories.items(), key=lambda x: x[1])[0] if categories else "None"
    }
