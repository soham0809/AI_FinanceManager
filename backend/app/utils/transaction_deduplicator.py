"""Transaction deduplication utilities"""
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class TransactionDeduplicator:
    def __init__(self):
        self.recent_transactions: List[Dict[str, Any]] = []
        self.max_history = 1000  # Keep last 1000 transactions for duplicate checking
    
    def generate_transaction_hash(self, transaction_data: Dict[str, Any]) -> str:
        """Generate hash for transaction based on key fields"""
        hash_string = f"{transaction_data.get('vendor', '')}-{transaction_data.get('amount', 0)}-{transaction_data.get('date', '')}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def is_duplicate_by_id(self, transaction_id: Optional[str]) -> bool:
        """Check if transaction ID already exists"""
        if not transaction_id:
            return False
        
        for recent_tx in self.recent_transactions:
            if recent_tx.get('transaction_id') == transaction_id:
                return True
        return False
    
    def is_duplicate_by_hash(self, transaction_hash: str) -> bool:
        """Check if transaction hash already exists"""
        for recent_tx in self.recent_transactions:
            if recent_tx.get('hash') == transaction_hash:
                return True
        return False
    
    def is_similar_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for similar transactions within time window"""
        current_amount = transaction_data.get('amount', 0)
        current_vendor = transaction_data.get('vendor', '').lower()
        current_date_str = transaction_data.get('date', '')
        
        try:
            current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            current_date = datetime.now()
        
        # Check for similar transactions within 1 hour
        time_window = timedelta(hours=1)
        
        for recent_tx in self.recent_transactions:
            recent_amount = recent_tx.get('amount', 0)
            recent_vendor = recent_tx.get('vendor', '').lower()
            recent_date_str = recent_tx.get('date', '')
            
            try:
                recent_date = datetime.strptime(recent_date_str, '%Y-%m-%d')
            except (ValueError, TypeError):
                continue
            
            # Check if amounts match and vendors are similar
            if (abs(current_amount - recent_amount) < 0.01 and 
                current_vendor == recent_vendor and
                abs((current_date - recent_date).total_seconds()) < time_window.total_seconds()):
                return recent_tx
        
        return None
    
    def is_duplicate(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive duplicate check"""
        transaction_id = transaction_data.get('transaction_id')
        
        # Check by transaction ID first (most reliable)
        if self.is_duplicate_by_id(transaction_id):
            return {
                'is_duplicate': True,
                'reason': f'Duplicate transaction ID: {transaction_id}',
                'method': 'transaction_id'
            }
        
        # Check by hash
        transaction_hash = self.generate_transaction_hash(transaction_data)
        if self.is_duplicate_by_hash(transaction_hash):
            return {
                'is_duplicate': True,
                'reason': 'Duplicate transaction hash',
                'method': 'hash'
            }
        
        # Check for similar transactions
        similar_tx = self.is_similar_transaction(transaction_data)
        if similar_tx:
            return {
                'is_duplicate': True,
                'reason': 'Similar transaction found within time window',
                'method': 'similarity',
                'similar_transaction': similar_tx
            }
        
        return {
            'is_duplicate': False,
            'reason': 'No duplicate found',
            'hash': transaction_hash
        }
    
    def add_transaction(self, transaction_data: Dict[str, Any]):
        """Add transaction to recent history for future duplicate checking"""
        transaction_hash = self.generate_transaction_hash(transaction_data)
        
        tx_record = {
            'vendor': transaction_data.get('vendor'),
            'amount': transaction_data.get('amount'),
            'date': transaction_data.get('date'),
            'transaction_type': transaction_data.get('transaction_type'),
            'transaction_id': transaction_data.get('transaction_id'),
            'hash': transaction_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        self.recent_transactions.append(tx_record)
        
        # Keep only recent transactions to prevent memory bloat
        if len(self.recent_transactions) > self.max_history:
            self.recent_transactions = self.recent_transactions[-self.max_history:]
    
    def clear_history(self):
        """Clear transaction history"""
        self.recent_transactions.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get deduplicator statistics"""
        return {
            'total_tracked': len(self.recent_transactions),
            'max_history': self.max_history,
            'oldest_transaction': self.recent_transactions[0]['timestamp'] if self.recent_transactions else None,
            'newest_transaction': self.recent_transactions[-1]['timestamp'] if self.recent_transactions else None
        }
