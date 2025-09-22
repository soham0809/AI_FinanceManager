import sqlite3
from datetime import datetime

# Connect to the database (using the correct database name)
conn = sqlite3.connect('financial_copilot.db')
cursor = conn.cursor()

# Check if transactions table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
if cursor.fetchone():
    # Delete transactions with future dates (beyond today)
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('DELETE FROM transactions WHERE date > ?', (today,))
    
    deleted_count = cursor.rowcount
    print(f'Deleted {deleted_count} future-dated transactions')
    
    # Also delete transactions from years 2025, 2026 which are clearly wrong
    cursor.execute('DELETE FROM transactions WHERE date LIKE "2025%" OR date LIKE "2026%"')
    deleted_future = cursor.rowcount
    print(f'Deleted {deleted_future} transactions from 2025/2026')
    
    # Show remaining transactions count
    cursor.execute('SELECT COUNT(*) FROM transactions')
    remaining = cursor.fetchone()[0]
    print(f'Remaining transactions: {remaining}')
else:
    print("Transactions table not found")

# Commit changes and close connection
conn.commit()
conn.close()

print("Database cleanup completed")
