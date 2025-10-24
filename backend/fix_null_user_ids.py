#!/usr/bin/env python3
"""
Fix NULL user_ids in transactions
Assign all NULL user_id transactions to user 1 (testuser)
"""
import sqlite3

def fix_null_user_ids():
    """Fix transactions with NULL user_id"""
    
    print("🔧 Fixing NULL user_ids in transactions...")
    
    conn = sqlite3.connect('financial_copilot.db')
    cursor = conn.cursor()
    
    try:
        # Check current state
        cursor.execute("SELECT user_id, COUNT(*) FROM transactions GROUP BY user_id")
        before_counts = cursor.fetchall()
        print("Before fix:")
        for row in before_counts:
            user_id = "NULL" if row[0] is None else row[0]
            print(f"  User ID {user_id}: {row[1]} transactions")
        
        # Update NULL user_ids to user 1
        cursor.execute("UPDATE transactions SET user_id = 1 WHERE user_id IS NULL")
        updated_count = cursor.rowcount
        print(f"\n✅ Updated {updated_count} transactions to user_id = 1")
        
        conn.commit()
        
        # Check after state
        cursor.execute("SELECT user_id, COUNT(*) FROM transactions GROUP BY user_id")
        after_counts = cursor.fetchall()
        print("\nAfter fix:")
        for row in after_counts:
            user_id = "NULL" if row[0] is None else row[0]
            print(f"  User ID {user_id}: {row[1]} transactions")
        
        print("\n✅ All transactions now have proper user_id assignment!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_null_user_ids()
