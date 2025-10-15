#!/usr/bin/env python3
"""
Fix the sms_text column constraint issue
"""

import sqlite3
from pathlib import Path

def fix_sms_text_constraint():
    """Fix the NOT NULL constraint on sms_text column"""
    db_path = Path("backend/financial_copilot.db")
    
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Fixing sms_text column constraint...")
        
        # Get current table schema
        cursor.execute("PRAGMA table_info(transactions)")
        columns_info = cursor.fetchall()
        
        print("📋 Current table schema:")
        for col in columns_info:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Create a new table with the correct schema
        cursor.execute("""
            CREATE TABLE transactions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sms_text TEXT,  -- Make this nullable
                vendor VARCHAR(255) NOT NULL,
                amount REAL NOT NULL,
                date DATETIME NOT NULL,
                category VARCHAR(100) NOT NULL,
                confidence REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                payment_method VARCHAR(50),
                is_subscription BOOLEAN DEFAULT 0,
                subscription_service VARCHAR(100),
                card_last_four VARCHAR(4),
                upi_transaction_id VARCHAR(255),
                merchant_category VARCHAR(100),
                is_recurring BOOLEAN DEFAULT 0,
                updated_at DATETIME,
                transaction_type VARCHAR(50) DEFAULT 'debit',
                success BOOLEAN DEFAULT 1,
                raw_text TEXT
            )
        """)
        
        # Copy existing data
        cursor.execute("""
            INSERT INTO transactions_new 
            SELECT id, sms_text, vendor, amount, date, category, confidence, created_at,
                   payment_method, is_subscription, subscription_service, card_last_four,
                   upi_transaction_id, merchant_category, is_recurring, updated_at,
                   transaction_type, success, raw_text
            FROM transactions
        """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE transactions")
        cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
        
        conn.commit()
        conn.close()
        
        print("✅ Fixed sms_text column constraint!")
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    fix_sms_text_constraint()
