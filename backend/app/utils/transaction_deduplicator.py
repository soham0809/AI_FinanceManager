"""Transaction deduplication utilities"""
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class TransactionDeduplicator:
    def __init__(self):
        self.recent_transactions: List[Dict[str, Any]] = []
        self.max_history = 1000  # Keep last 1000 transactions for duplicate checking
    
    def generate_fingerprint(
        self, 
        sender: str, 
        sms_text: str, 
        device_timestamp: int
    ) -> str:
        """
        Create unique fingerprint for SMS using sender + timestamp + normalized text.
        This is FAST and happens BEFORE any LLM call.
        
        Args:
            sender: SMS sender address (e.g., "AD-HDFCBK")
            sms_text: SMS body text
            device_timestamp: Milliseconds since epoch when SMS was received
            
        Returns:
            MD5 hash string (32 chars)
        """
        # Normalize text: lowercase, remove extra whitespace, limit to 100 chars
        clean_text = ' '.join(sms_text.lower().split())[:100]
        
        # Create unique string combining all identifiers
        unique_string = f"{sender or 'unknown'}_{device_timestamp}_{clean_text}"
        
        # MD5 hash (fast, collision-resistant enough for dedup)
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def is_duplicate_by_fingerprint(self, fingerprint: str, db_session) -> bool:
        """
        Check if fingerprint exists in database.
        This is a fast indexed query - O(log n).
        
        Args:
            fingerprint: MD5 hash to check
            db_session: SQLAlchemy session
            
        Returns:
            True if duplicate exists
        """
        from app.models.transaction import Transaction
        
        exists = db_session.query(Transaction).filter(
            Transaction.fingerprint == fingerprint
        ).first()
        
        return exists is not None
    
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
        current_timestamp = datetime.now()
        
        # Also get SMS text for better matching
        current_sms = transaction_data.get('sms_text', '').lower()
        
        # Check for similar transactions within 1 minute (as requested)
        time_window = timedelta(minutes=1)
        
        for recent_tx in self.recent_transactions:
            recent_amount = recent_tx.get('amount', 0)
            recent_vendor = recent_tx.get('vendor', '').lower()
            recent_sms = recent_tx.get('sms_text', '').lower()
            
            try:
                # Use the timestamp when transaction was processed
                recent_timestamp = datetime.fromisoformat(recent_tx.get('timestamp', ''))
            except (ValueError, TypeError):
                continue
            
            # Check for duplicates based on multiple criteria:
            # 1. Same amount (exact match)
            # 2. Same vendor (case-insensitive)
            # 3. Similar SMS text (70% similarity) OR exact vendor match
            # 4. Within 1-minute time window
            
            amount_match = abs(current_amount - recent_amount) < 0.01
            vendor_match = current_vendor == recent_vendor
            
            # Calculate SMS similarity (simple approach)
            sms_similarity = 0.0
            if current_sms and recent_sms:
                common_words = set(current_sms.split()) & set(recent_sms.split())
                total_words = len(set(current_sms.split()) | set(recent_sms.split()))
                if total_words > 0:
                    sms_similarity = len(common_words) / total_words
            
            time_diff = abs((current_timestamp - recent_timestamp).total_seconds())
            time_match = time_diff < time_window.total_seconds()
            
            # Consider it a duplicate if:
            # - Amounts match AND vendors match AND within time window
            # - OR amounts match AND SMS similarity > 70% AND within time window
            is_duplicate = (
                (amount_match and vendor_match and time_match) or
                (amount_match and sms_similarity > 0.7 and time_match)
            )
            
            if is_duplicate:
                return {
                    **recent_tx,
                    'duplicate_reason': f'Amount: {amount_match}, Vendor: {vendor_match}, SMS: {sms_similarity:.2f}, Time: {time_diff:.0f}s'
                }
        
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
            'sms_text': transaction_data.get('sms_text'),
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
