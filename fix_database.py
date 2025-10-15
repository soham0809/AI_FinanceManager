#!/usr/bin/env python3
"""
Database Migration Script for AI Finance Manager
Ensures all required columns exist in the database
"""

import sqlite3
import os
from pathlib import Path

def fix_database():
    """Add missing columns to existing database"""
    db_path = Path("backend/financial_copilot.db")
    
    if not db_path.exists():
        print("✅ No existing database found - will be created fresh")
        return True
    
    print(f"🔧 Fixing database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(transactions)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Existing columns: {existing_columns}")
        
        # Define new columns that might be missing
        new_columns = [
            ("payment_method", "VARCHAR(50)"),
            ("is_subscription", "BOOLEAN DEFAULT 0"),
            ("subscription_service", "VARCHAR(100)"),
            ("card_last_four", "VARCHAR(4)"),
            ("upi_transaction_id", "VARCHAR(255)"),
            ("merchant_category", "VARCHAR(100)"),
            ("is_recurring", "BOOLEAN DEFAULT 0"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "DATETIME")
        ]
        
        # Add missing columns
        added_columns = []
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE transactions ADD COLUMN {column_name} {column_type}")
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"⚠️  Warning adding {column_name}: {e}")
        
        # Create categories table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                color VARCHAR(7),
                icon VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default categories if table is empty
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            default_categories = [
                ("Food & Dining", "Restaurant and food delivery expenses", "#FF6B6B", "🍽️"),
                ("Transportation", "Travel and commute expenses", "#4ECDC4", "🚗"),
                ("Shopping", "Online and offline shopping", "#45B7D1", "🛍️"),
                ("Entertainment", "Movies, games, and leisure", "#96CEB4", "🎬"),
                ("Bills & Utilities", "Monthly bills and utilities", "#FFEAA7", "💡"),
                ("Healthcare", "Medical and health expenses", "#DDA0DD", "🏥"),
                ("Education", "Learning and course expenses", "#98D8C8", "📚"),
                ("Others", "Miscellaneous expenses", "#F7DC6F", "📦")
            ]
            
            cursor.executemany(
                "INSERT INTO categories (name, description, color, icon) VALUES (?, ?, ?, ?)",
                default_categories
            )
            print("✅ Added default categories")
        
        conn.commit()
        conn.close()
        
        if added_columns:
            print(f"✅ Database updated successfully! Added {len(added_columns)} columns: {', '.join(added_columns)}")
        else:
            print("✅ Database is already up to date")
        
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 AI Finance Manager - Database Migration")
    print("=" * 50)
    
    if fix_database():
        print("🎉 Database migration completed successfully!")
    else:
        print("❌ Database migration failed!")
