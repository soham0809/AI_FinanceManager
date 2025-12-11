"""Batch transaction processor for re-processing existing transactions with Ollama"""
import time
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.transaction import Transaction
from app.models.user import User
from app.utils.ollama_integration import OllamaAssistant
from app.config.database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchTransactionProcessor:
    def __init__(self, batch_size: int = 2, delay_between_batches: int = 8):
        """Initialize batch processor
        
        Args:
            batch_size: Number of transactions to process in each batch
            delay_between_batches: Delay in seconds between batches to avoid overwhelming Ollama (increased for stability)
        """
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.ollama_assistant = OllamaAssistant()
        
    def get_transactions_for_processing(self, db: Session, limit: Optional[int] = None) -> List[Transaction]:
        """Get transactions that need processing/re-processing
        
        Args:
            db: Database session
            limit: Maximum number of transactions to fetch
            
        Returns:
            List of transactions to process
        """
        query = db.query(Transaction).filter(
            Transaction.sms_text.isnot(None),  # Has SMS text
            Transaction.sms_text != ""         # SMS text is not empty
        ).order_by(Transaction.created_at.desc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def process_single_transaction(self, transaction: Transaction, db: Session) -> Dict[str, Any]:
        """Process a single transaction with Ollama
        
        Args:
            transaction: Transaction object to process
            db: Database session
            
        Returns:
            Processing result dictionary
        """
        try:
            logger.info(f"Processing transaction ID {transaction.id}: {transaction.sms_text[:50]}...")
            
            # Parse with Ollama
            result = self.ollama_assistant.parse_sms_transaction(transaction.sms_text)
            
            if result['success']:
                transaction_data = result['transaction_data']
                
                # Store original values for comparison
                original_data = {
                    'vendor': transaction.vendor,
                    'amount': transaction.amount,
                    'date': transaction.date,
                    'transaction_type': getattr(transaction, 'transaction_type', 'debit'),
                    'category': transaction.category,
                    'confidence': transaction.confidence
                }
                
                # Update transaction with new data
                updates_made = []
                
                # Update vendor
                new_vendor = transaction_data.get('vendor', '').strip()
                if new_vendor and new_vendor != transaction.vendor:
                    transaction.vendor = new_vendor
                    updates_made.append(f"vendor: '{original_data['vendor']}' -> '{new_vendor}'")
                
                # Update amount
                new_amount = transaction_data.get('amount')
                if new_amount and abs(float(new_amount) - float(transaction.amount)) > 0.01:
                    transaction.amount = float(new_amount)
                    updates_made.append(f"amount: {original_data['amount']} -> {new_amount}")
                
                # Update transaction type
                new_type = transaction_data.get('transaction_type', '').lower()
                current_type = getattr(transaction, 'transaction_type', 'debit')
                if new_type and new_type != current_type:
                    transaction.transaction_type = new_type
                    updates_made.append(f"type: '{current_type}' -> '{new_type}'")
                
                # Update category
                new_category = transaction_data.get('category', '')
                if new_category and new_category != transaction.category:
                    transaction.category = new_category
                    updates_made.append(f"category: '{original_data['category']}' -> '{new_category}'")
                
                # Update date if provided and different
                new_date = transaction_data.get('date')
                if new_date and new_date != 'null':
                    try:
                        parsed_date = datetime.strptime(new_date, '%Y-%m-%d')
                        # Handle both datetime and string dates
                        current_date = transaction.date if isinstance(transaction.date, datetime) else datetime.strptime(str(transaction.date), '%Y-%m-%d')
                        if parsed_date.date() != current_date.date():
                            transaction.date = parsed_date
                            updates_made.append(f"date: {current_date.date()} -> {parsed_date.date()}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Could not parse date: {new_date}, error: {e}")
                
                # Update confidence
                new_confidence = transaction_data.get('confidence', 0.0)
                if abs(float(new_confidence) - float(transaction.confidence)) > 0.01:
                    transaction.confidence = float(new_confidence)
                    updates_made.append(f"confidence: {original_data['confidence']} -> {new_confidence}")
                
                # Update transaction_id if available
                new_transaction_id = transaction_data.get('transaction_id')
                if new_transaction_id and new_transaction_id != 'null':
                    if not hasattr(transaction, 'transaction_id') or transaction.transaction_id != new_transaction_id:
                        transaction.transaction_id = new_transaction_id
                        updates_made.append(f"transaction_id: -> '{new_transaction_id}'")
                
                # Update timestamp
                transaction.updated_at = datetime.now()
                
                # Commit changes
                db.commit()
                db.refresh(transaction)
                
                return {
                    'success': True,
                    'transaction_id': transaction.id,
                    'updates_made': updates_made,
                    'confidence': new_confidence,
                    'processing_time': time.time()
                }
                
            else:
                # Handle failed parsing
                if result.get('is_promotional'):
                    logger.info(f"Transaction ID {transaction.id} identified as promotional")
                    return {
                        'success': True,
                        'transaction_id': transaction.id,
                        'updates_made': [],
                        'note': 'Identified as promotional/non-transaction',
                        'processing_time': time.time()
                    }
                else:
                    logger.warning(f"Failed to process transaction ID {transaction.id}: {result.get('error')}")
                    return {
                        'success': False,
                        'transaction_id': transaction.id,
                        'error': result.get('error'),
                        'processing_time': time.time()
                    }
                    
        except Exception as e:
            logger.error(f"Exception processing transaction ID {transaction.id}: {e}")
            return {
                'success': False,
                'transaction_id': transaction.id,
                'error': str(e),
                'processing_time': time.time()
            }
    
    def process_batch(self, transactions: List[Transaction], db: Session) -> Dict[str, Any]:
        """Process a batch of transactions
        
        Args:
            transactions: List of transactions to process
            db: Database session
            
        Returns:
            Batch processing results
        """
        batch_start_time = time.time()
        results = []
        
        for transaction in transactions:
            start_time = time.time()
            result = self.process_single_transaction(transaction, db)
            result['processing_time'] = time.time() - start_time
            results.append(result)
            
            # Small delay between individual transactions
            time.sleep(0.5)
        
        batch_processing_time = time.time() - batch_start_time
        
        # Calculate statistics
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        total_updates = sum(len(r.get('updates_made', [])) for r in results)
        
        return {
            'batch_size': len(transactions),
            'successful': successful,
            'failed': failed,
            'total_updates': total_updates,
            'processing_time': batch_processing_time,
            'results': results
        }
    
    def process_all_transactions(self, db: Session, limit: Optional[int] = None) -> Dict[str, Any]:
        """Process all transactions in batches
        
        Args:
            db: Database session
            limit: Maximum number of transactions to process
            
        Returns:
            Overall processing results
        """
        logger.info("Starting batch transaction processing...")
        overall_start_time = time.time()
        
        # Get transactions to process
        transactions = self.get_transactions_for_processing(db, limit)
        total_transactions = len(transactions)
        
        if total_transactions == 0:
            logger.info("No transactions found for processing")
            return {
                'success': True,
                'total_transactions': 0,
                'message': 'No transactions to process'
            }
        
        logger.info(f"Found {total_transactions} transactions to process")
        
        # Process in batches
        all_results = []
        processed_count = 0
        total_successful = 0
        total_failed = 0
        total_updates = 0
        
        for i in range(0, total_transactions, self.batch_size):
            batch_transactions = transactions[i:i + self.batch_size]
            batch_number = (i // self.batch_size) + 1
            total_batches = (total_transactions + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processing batch {batch_number}/{total_batches} ({len(batch_transactions)} transactions)")
            
            # Process batch
            batch_result = self.process_batch(batch_transactions, db)
            all_results.append(batch_result)
            
            # Update counters
            processed_count += batch_result['batch_size']
            total_successful += batch_result['successful']
            total_failed += batch_result['failed']
            total_updates += batch_result['total_updates']
            
            # Progress update
            progress = (processed_count / total_transactions) * 100
            logger.info(f"Progress: {processed_count}/{total_transactions} ({progress:.1f}%) - "
                       f"Successful: {batch_result['successful']}, Failed: {batch_result['failed']}, "
                       f"Updates: {batch_result['total_updates']}")
            
            # Delay between batches (except for the last batch)
            if i + self.batch_size < total_transactions:
                logger.info(f"Waiting {self.delay_between_batches} seconds before next batch...")
                time.sleep(self.delay_between_batches)
        
        overall_processing_time = time.time() - overall_start_time
        
        # Final summary
        logger.info(f"Batch processing completed!")
        logger.info(f"Total processed: {processed_count}")
        logger.info(f"Successful: {total_successful}")
        logger.info(f"Failed: {total_failed}")
        logger.info(f"Total updates made: {total_updates}")
        logger.info(f"Total processing time: {overall_processing_time:.2f} seconds")
        
        return {
            'success': True,
            'total_transactions': total_transactions,
            'processed': processed_count,
            'successful': total_successful,
            'failed': total_failed,
            'total_updates': total_updates,
            'processing_time': overall_processing_time,
            'batches': all_results
        }
