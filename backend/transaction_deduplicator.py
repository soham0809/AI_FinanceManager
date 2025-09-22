"""
Transaction deduplication module to handle duplicate SMS messages and transactions
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)

class TransactionDeduplicator:
    """Handles detection and prevention of duplicate transactions"""
    
    def __init__(self):
        self.recent_transactions = []  # Store recent transactions for comparison
        self.max_history_hours = 24  # Keep transactions for 24 hours for duplicate detection
    
    def generate_transaction_hash(self, transaction_data: Dict[str, Any]) -> str:
        """Generate a unique hash for transaction based on key fields"""
        # Use amount, vendor, and date for hash generation
        hash_string = f"{transaction_data.get('amount', 0)}-{transaction_data.get('vendor', '')}-{transaction_data.get('date', '')}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def is_duplicate_by_hash(self, transaction_data: Dict[str, Any]) -> bool:
        """Check if transaction is duplicate based on hash"""
        transaction_hash = self.generate_transaction_hash(transaction_data)
        
        # Check against recent transactions
        for recent in self.recent_transactions:
            if recent.get('hash') == transaction_hash:
                return True
        return False
    
    def is_duplicate_by_transaction_id(self, transaction_data: Dict[str, Any]) -> bool:
        """Check if transaction is duplicate based on UPI/transaction ID"""
        transaction_id = transaction_data.get('transaction_id')
        if not transaction_id or transaction_id == 'null':
            return False
        
        # Check against recent transactions
        for recent in self.recent_transactions:
            if recent.get('transaction_id') == transaction_id:
                return True
        return False
    
    def is_duplicate_by_similarity(self, transaction_data: Dict[str, Any]) -> bool:
        """Check for duplicate based on amount, vendor, and time proximity"""
        amount = transaction_data.get('amount')
        vendor = transaction_data.get('vendor', '').lower()
        transaction_date = transaction_data.get('date')
        
        if not amount or not vendor:
            return False
        
        try:
            trans_datetime = datetime.fromisoformat(transaction_date.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            trans_datetime = datetime.now()
        
        # Check against recent transactions
        for recent in self.recent_transactions:
            recent_amount = recent.get('amount')
            recent_vendor = recent.get('vendor', '').lower()
            recent_date = recent.get('date')
            
            if not recent_amount or not recent_vendor:
                continue
            
            try:
                recent_datetime = datetime.fromisoformat(recent_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                continue
            
            # Check if amounts match and vendors are similar
            if (abs(amount - recent_amount) < 0.01 and 
                vendor == recent_vendor and
                abs((trans_datetime - recent_datetime).total_seconds()) < 3600):  # Within 1 hour
                return True
        
        return False
    
    def is_duplicate(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive duplicate detection"""
        # Clean old transactions first
        self._cleanup_old_transactions()
        
        # Check by transaction ID first (most reliable)
        if self.is_duplicate_by_transaction_id(transaction_data):
            return {
                'is_duplicate': True,
                'reason': 'Duplicate transaction ID/UPI reference',
                'method': 'transaction_id'
            }
        
        # Check by hash
        if self.is_duplicate_by_hash(transaction_data):
            return {
                'is_duplicate': True,
                'reason': 'Duplicate transaction hash',
                'method': 'hash'
            }
        
        # Check by similarity
        if self.is_duplicate_by_similarity(transaction_data):
            return {
                'is_duplicate': True,
                'reason': 'Similar transaction within 1 hour',
                'method': 'similarity'
            }
        
        return {
            'is_duplicate': False,
            'reason': 'No duplicate found'
        }
    
    def add_transaction(self, transaction_data: Dict[str, Any]) -> None:
        """Add transaction to recent transactions for future duplicate detection"""
        transaction_record = {
            'amount': transaction_data.get('amount'),
            'vendor': transaction_data.get('vendor'),
            'date': transaction_data.get('date'),
            'transaction_id': transaction_data.get('transaction_id'),
            'hash': self.generate_transaction_hash(transaction_data),
            'added_at': datetime.now().isoformat()
        }
        
        self.recent_transactions.append(transaction_record)
        
        # Keep only recent transactions to prevent memory bloat
        if len(self.recent_transactions) > 1000:
            self.recent_transactions = self.recent_transactions[-500:]
    
    def _cleanup_old_transactions(self) -> None:
        """Remove transactions older than max_history_hours"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_history_hours)
        
        self.recent_transactions = [
            trans for trans in self.recent_transactions
            if datetime.fromisoformat(trans.get('added_at', '1970-01-01T00:00:00')) > cutoff_time
        ]
    
    def get_duplicate_stats(self) -> Dict[str, Any]:
        """Get statistics about duplicate detection"""
        return {
            'recent_transactions_count': len(self.recent_transactions),
            'oldest_transaction': min([t.get('added_at') for t in self.recent_transactions]) if self.recent_transactions else None,
            'newest_transaction': max([t.get('added_at') for t in self.recent_transactions]) if self.recent_transactions else None
        }

# Global deduplicator instance
transaction_deduplicator = TransactionDeduplicator()
