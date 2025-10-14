#!/usr/bin/env python3
"""
Script to fix incorrect dates in the transaction database.
This will correct any transactions with future dates (2026+) to 2025.
"""

import sqlite3
from datetime import datetime
import os

def fix_transaction_dates():
    """Fix incorrect future dates in transactions"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'transactions.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find transactions with future dates
        current_year = datetime.now().year
        cursor.execute("""
            SELECT id, date, vendor, amount 
            FROM transactions 
            WHERE strftime('%Y', date) > ?
        """, (str(current_year),))
        
        future_transactions = cursor.fetchall()
        
        if not future_transactions:
            print("✅ No transactions with future dates found!")
            conn.close()
            return
        
        print(f"🔍 Found {len(future_transactions)} transactions with future dates:")
        
        fixed_count = 0
        for transaction in future_transactions:
            tid, date_str, vendor, amount = transaction
            
            try:
                # Parse the date
                date_obj = datetime.fromisoformat(date_str.replace('T', ' ').split('.')[0])
                
                # If year is 2026 or later, change to 2025
                if date_obj.year > current_year:
                    corrected_date = date_obj.replace(year=current_year)
                    corrected_date_str = corrected_date.strftime('%Y-%m-%d %H:%M:%S')
                    
                    print(f"  📝 ID {tid}: {vendor} - {date_str} → {corrected_date_str}")
                    
                    # Update the database
                    cursor.execute("""
                        UPDATE transactions 
                        SET date = ? 
                        WHERE id = ?
                    """, (corrected_date_str, tid))
                    
                    fixed_count += 1
                    
            except Exception as e:
                print(f"  ❌ Error fixing transaction {tid}: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print(f"\n✅ Successfully fixed {fixed_count} transactions!")
        print("🔄 Restart your backend server to see the changes.")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("=== TRANSACTION DATE FIXER ===")
    print("This script will fix any transactions with future dates (2026+)")
    print()
    
    fix_transaction_dates()
