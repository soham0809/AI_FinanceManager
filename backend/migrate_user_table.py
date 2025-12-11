"""
Database migration script to add refresh token columns to users table
Run this script to update the existing database schema
"""
import sqlite3
import os
from datetime import datetime

def migrate_user_table():
    """Add refresh token columns to users table"""
    db_path = "financial_copilot.db"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Creating new database...")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in users table: {columns}")
        
        # Add refresh_token column if it doesn't exist
        if 'refresh_token' not in columns:
            print("Adding refresh_token column...")
            cursor.execute("ALTER TABLE users ADD COLUMN refresh_token TEXT")
            print("✅ refresh_token column added")
        else:
            print("✅ refresh_token column already exists")
        
        # Add refresh_token_expires_at column if it doesn't exist
        if 'refresh_token_expires_at' not in columns:
            print("Adding refresh_token_expires_at column...")
            cursor.execute("ALTER TABLE users ADD COLUMN refresh_token_expires_at DATETIME")
            print("✅ refresh_token_expires_at column added")
        else:
            print("✅ refresh_token_expires_at column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns in users table: {updated_columns}")
        
        # Show current users count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Total users in database: {user_count}")
        
        conn.close()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_user_table()
    print("🎉 Migration process completed!")
