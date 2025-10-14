"""Script to run batch processing of existing transactions with Ollama"""
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.utils.batch_processor import BatchTransactionProcessor
from backend.app.config.database import get_db

def main():
    """Main function to run batch processing"""
    print("=" * 80)
    print("BATCH TRANSACTION PROCESSING WITH OLLAMA")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize batch processor
        # Using smaller batch size (3) and longer delays (5s) to be gentle on Ollama
        processor = BatchTransactionProcessor(batch_size=3, delay_between_batches=5)
        
        print("Configuration:")
        print(f"  Batch size: {processor.batch_size} transactions per batch")
        print(f"  Delay between batches: {processor.delay_between_batches} seconds")
        print(f"  Ollama host: {processor.ollama_assistant.host}")
        print()
        
        # Ask user for confirmation
        response = input("Do you want to proceed with batch processing? (y/N): ").strip().lower()
        if response != 'y':
            print("Batch processing cancelled.")
            return
        
        # Ask for limit
        limit_input = input("Enter max number of transactions to process (press Enter for all): ").strip()
        limit = None
        if limit_input:
            try:
                limit = int(limit_input)
                print(f"Processing up to {limit} transactions")
            except ValueError:
                print("Invalid limit, processing all transactions")
        
        print("\nStarting batch processing...")
        print("-" * 80)
        
        # Run batch processing
        result = processor.process_all_transactions(db, limit=limit)
        
        # Display results
        print("\n" + "=" * 80)
        print("BATCH PROCESSING RESULTS")
        print("=" * 80)
        
        if result['success']:
            print(f"✓ Total transactions processed: {result['processed']}")
            print(f"✓ Successful: {result['successful']}")
            print(f"✗ Failed: {result['failed']}")
            print(f"📝 Total updates made: {result['total_updates']}")
            print(f"⏱️  Total processing time: {result['processing_time']:.2f} seconds")
            
            if result['successful'] > 0:
                avg_time = result['processing_time'] / result['successful']
                print(f"⏱️  Average time per transaction: {avg_time:.2f} seconds")
            
            # Show detailed results for transactions with updates
            print("\n" + "-" * 80)
            print("DETAILED UPDATES")
            print("-" * 80)
            
            total_detailed_updates = 0
            for batch in result['batches']:
                for transaction_result in batch['results']:
                    if transaction_result['success'] and transaction_result.get('updates_made'):
                        total_detailed_updates += len(transaction_result['updates_made'])
                        print(f"\nTransaction ID {transaction_result['transaction_id']}:")
                        for update in transaction_result['updates_made']:
                            print(f"  • {update}")
            
            if total_detailed_updates == 0:
                print("No updates were needed - all transactions were already accurate!")
            
        else:
            print(f"✗ Batch processing failed: {result.get('message', 'Unknown error')}")
        
        print("\n" + "=" * 80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Critical error during batch processing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
