#!/usr/bin/env python3
"""
Check Transaction in Database
"""
import sqlite3

def check_transaction():
    """Check the latest transaction in database"""
    
    conn = sqlite3.connect('financial_copilot.db')
    cursor = conn.cursor()
    
    # Get the latest transaction
    cursor.execute("SELECT id, vendor, amount, user_id FROM transactions ORDER BY id DESC LIMIT 5")
    results = cursor.fetchall()
    
    print("Latest 5 transactions:")
    for row in results:
        print(f"  ID: {row[0]}, Vendor: {row[1]}, Amount: {row[2]}, User ID: {row[3]}")
    
    # Check specific transaction
    cursor.execute("SELECT id, vendor, amount, user_id FROM transactions WHERE vendor = 'TEST SCAN'")
    test_trans = cursor.fetchall()
    
    print(f"\nTEST SCAN transactions:")
    for row in test_trans:
        print(f"  ID: {row[0]}, Vendor: {row[1]}, Amount: {row[2]}, User ID: {row[3]}")
    
    # Check user_id distribution
    cursor.execute("SELECT user_id, COUNT(*) FROM transactions GROUP BY user_id")
    user_counts = cursor.fetchall()
    
    print(f"\nTransactions per user:")
    for row in user_counts:
        print(f"  User ID {row[0]}: {row[1]} transactions")
    
    conn.close()

if __name__ == "__main__":
    check_transaction()
