from database import DatabaseManager
from datetime import datetime

# Initialize database manager
db = DatabaseManager()

# Get recent transactions
transactions = db.get_transactions(limit=10)

print("Recent transactions from database:")
for t in transactions[:5]:
    print(f"Vendor: {t.vendor}, Date: {t.date}, Amount: {t.amount}")

# Check for future dates
future_count = 0
current_date = datetime.now().date()
for t in transactions:
    # Convert datetime to date for comparison
    transaction_date = t.date.date() if hasattr(t.date, 'date') else t.date
    if transaction_date > current_date:
        future_count += 1

print(f"\nTotal transactions: {len(transactions)}")
print(f"Future-dated transactions: {future_count}")

# Also check for 2025/2026 dates specifically
future_years_count = 0
for t in transactions:
    if t.date.year >= 2025:
        future_years_count += 1
        
print(f"Transactions from 2025/2026: {future_years_count}")
