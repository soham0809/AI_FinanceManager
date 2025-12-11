"""
Intelligent Query Cache System
Pre-processes common financial queries using parsed transactions as data store
Caches results for fast retrieval without hitting LLM repeatedly
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.transaction import Transaction
from app.utils.ollama_integration import OllamaAssistant
import hashlib

class IntelligentQueryCache:
    def __init__(self):
        self.ollama = OllamaAssistant()
        self.cache_duration = 3600  # 1 hour cache
        self.query_cache: Dict[str, Any] = {}
        
        # Pre-defined common queries to auto-cache
        self.common_queries = [
            "What are my top 5 spending categories this month?",
            "How much did I spend on subscriptions?",
            "What's my average daily spending?",
            "Which vendor do I spend the most money with?",
            "What's my spending trend compared to last month?",
            "How much did I spend on food and dining?"
        ]
    
    def _generate_cache_key(self, query: str, user_id: int) -> str:
        """Generate unique cache key for query and user"""
        combined = f"{user_id}_{query.lower().strip()}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        
        cache_time = datetime.fromisoformat(cache_entry.get('timestamp', ''))
        return (datetime.now() - cache_time).seconds < self.cache_duration
    
    def _prepare_transaction_context(self, db: Session, user_id: int) -> str:
        """Prepare transaction data as context for LLM"""
        cutoff = datetime.now() - timedelta(days=30)
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            or_(
                and_(Transaction.date.isnot(None), Transaction.date >= cutoff),
                and_(Transaction.date.is_(None), Transaction.created_at >= cutoff)
            )
        ).order_by(Transaction.created_at.desc()).limit(100).all()
        
        if not transactions:
            return "No transaction data available for the last 30 days."
        
        # Create structured context
        context_data = {
            "total_transactions": len(transactions),
            "date_range": {
                "from": transactions[-1].created_at.strftime("%Y-%m-%d") if transactions else None,
                "to": transactions[0].created_at.strftime("%Y-%m-%d") if transactions else None
            },
            "transactions": []
        }
        
        for tx in transactions:
            tx_data = {
                "vendor": tx.vendor or "Unknown",
                "amount": float(tx.amount) if tx.amount else 0,
                "category": tx.category or "Others",
                "date": tx.date or tx.created_at.strftime("%Y-%m-%d"),
                "type": getattr(tx, 'transaction_type', 'debit')
            }
            context_data["transactions"].append(tx_data)
        
        # Create readable context for LLM
        context = f"""
FINANCIAL DATA SUMMARY:
- Total Transactions: {context_data['total_transactions']}
- Date Range: {context_data['date_range']['from']} to {context_data['date_range']['to']}

RECENT TRANSACTIONS:
"""
        
        for tx in context_data["transactions"][:20]:  # Show recent 20
            context += f"- {tx['date']}: {tx['vendor']} - Rs.{tx['amount']} ({tx['category']})\n"
        
        # Add category summary
        categories = {}
        total_spending = 0
        for tx in context_data["transactions"]:
            # Only count debit (spend) to avoid inflating with income
            if tx['amount'] > 0 and tx.get('type', 'debit') == 'debit':
                categories[tx['category']] = categories.get(tx['category'], 0) + tx['amount']
                total_spending += tx['amount']
        
        context += f"\nCATEGORY SUMMARY:\n"
        for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            context += f"- {category}: Rs.{amount:.2f} ({percentage:.1f}%)\n"
        
        context += f"\nTOTAL SPENDING: Rs.{total_spending:.2f}"
        
        return context
    
    async def _query_llm_with_context(self, query: str, context: str) -> str:
        """Query LLM with transaction context"""
        prompt = f"""
You are a financial assistant analyzing user's transaction data. Answer the user's question based on the provided financial data.

FINANCIAL DATA:
{context}

USER QUESTION: {query}

Please provide a helpful, specific answer based on the transaction data above. Include relevant numbers, percentages, and insights. Keep the response concise but informative.
"""
        
        try:
            response = await self.ollama.generate_response(prompt)
            return response.get('response', 'Unable to analyze the data at this time.')
        except Exception as e:
            # Fall back gracefully to a brief analytical message
            return f"I analyzed your recent transactions and can answer questions about your last 30 days of spending. (Detail unavailable: {str(e)})"
    
    async def get_cached_response(self, query: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Get cached response or generate new one"""
        cache_key = self._generate_cache_key(query, user_id)
        
        # Check cache first
        if cache_key in self.query_cache:
            cache_entry = self.query_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                return {
                    "response": cache_entry["response"],
                    "cached": True,
                    "timestamp": cache_entry["timestamp"],
                    "processing_time": 0
                }
        
        # Generate new response
        start_time = datetime.now()
        context = self._prepare_transaction_context(db, user_id)
        llm_response = await self._query_llm_with_context(query, context)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Cache the response
        cache_entry = {
            "response": llm_response,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "user_id": user_id
        }
        self.query_cache[cache_key] = cache_entry
        
        return {
            "response": llm_response,
            "cached": False,
            "timestamp": cache_entry["timestamp"],
            "processing_time": processing_time
        }
    
    async def pre_cache_common_queries(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Pre-cache common financial queries for faster access"""
        results = {
            "pre_cached_queries": [],
            "total_processing_time": 0,
            "cache_status": "success"
        }
        
        start_time = datetime.now()
        
        try:
            for query in self.common_queries:
                cache_key = self._generate_cache_key(query, user_id)
                
                # Only cache if not already cached
                if cache_key not in self.query_cache or not self._is_cache_valid(self.query_cache[cache_key]):
                    response = await self.get_cached_response(query, user_id, db)
                    results["pre_cached_queries"].append({
                        "query": query,
                        "cached": True,
                        "processing_time": response["processing_time"]
                    })
            
            results["total_processing_time"] = (datetime.now() - start_time).total_seconds()
            
        except Exception as e:
            results["cache_status"] = "error"
            results["error"] = str(e)
        
        return results
    
    def get_cache_stats(self, user_id: int) -> Dict[str, Any]:
        """Get cache statistics for user"""
        user_cache_entries = [
            entry for entry in self.query_cache.values() 
            if entry.get("user_id") == user_id
        ]
        
        valid_entries = [
            entry for entry in user_cache_entries 
            if self._is_cache_valid(entry)
        ]
        
        return {
            "total_cached_queries": len(user_cache_entries),
            "valid_cached_queries": len(valid_entries),
            "cache_hit_rate": len(valid_entries) / len(user_cache_entries) * 100 if user_cache_entries else 0,
            "common_queries_cached": len([
                entry for entry in valid_entries 
                if entry.get("query") in self.common_queries
            ]),
            "cache_duration_hours": self.cache_duration / 3600
        }
    
    def clear_user_cache(self, user_id: int) -> int:
        """Clear cache for specific user"""
        keys_to_remove = [
            key for key, entry in self.query_cache.items() 
            if entry.get("user_id") == user_id
        ]
        
        for key in keys_to_remove:
            del self.query_cache[key]
        
        return len(keys_to_remove)
    
    def clear_expired_cache(self) -> int:
        """Clear all expired cache entries"""
        keys_to_remove = [
            key for key, entry in self.query_cache.items() 
            if not self._is_cache_valid(entry)
        ]
        
        for key in keys_to_remove:
            del self.query_cache[key]
        
        return len(keys_to_remove)
