#!/usr/bin/env python3
"""
Schema Fix Script - Align database with model expectations
"""

import sqlite3
from pathlib import Path

def fix_schema():
    """Fix schema mismatches between database and model"""
    db_path = Path("backend/financial_copilot.db")
    
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current schema
        cursor.execute("PRAGMA table_info(transactions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"📋 Current columns: {list(columns.keys())}")
        
        # Required columns based on model
        required_columns = [
            ("transaction_type", "VARCHAR(50) DEFAULT 'debit'"),
            ("success", "BOOLEAN DEFAULT 1"),
            ("raw_text", "TEXT")
        ]
        
        # Add missing required columns
        for col_name, col_def in required_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_def}")
                    print(f"✅ Added required column: {col_name}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Warning: {e}")
        
        # If sms_text exists but raw_text doesn't, copy data
        if 'sms_text' in columns and 'raw_text' not in columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN raw_text TEXT")
            cursor.execute("UPDATE transactions SET raw_text = sms_text WHERE raw_text IS NULL")
            print("✅ Copied sms_text to raw_text")
        
        # Set default values for existing records
        cursor.execute("UPDATE transactions SET transaction_type = 'debit' WHERE transaction_type IS NULL")
        cursor.execute("UPDATE transactions SET success = 1 WHERE success IS NULL")
        
        conn.commit()
        conn.close()
        
        print("✅ Schema fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        return False

if __name__ == "__main__":
    fix_schema()
