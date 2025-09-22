from database import DatabaseManager, SessionLocal, Transaction
from datetime import datetime

# Initialize database manager
db = DatabaseManager()
session = SessionLocal()

try:
    # Delete all transactions with future dates (2025 and beyond)
    future_transactions = session.query(Transaction).filter(
        Transaction.date >= datetime(2025, 1, 1)
    ).all()
    
    print(f"Found {len(future_transactions)} future-dated transactions")
    
    for transaction in future_transactions:
        print(f"Deleting: {transaction.vendor} - {transaction.date}")
        session.delete(transaction)
    
    # Commit the changes
    session.commit()
    print("Successfully deleted future-dated transactions")
    
    # Verify cleanup
    remaining = session.query(Transaction).count()
    print(f"Remaining transactions: {remaining}")
    
    # Show recent transactions
    recent = session.query(Transaction).order_by(Transaction.date.desc()).limit(5).all()
    print("\nRecent transactions after cleanup:")
    for t in recent:
        print(f"Vendor: {t.vendor}, Date: {t.date}, Amount: {t.amount}")
        
finally:
    session.close()
