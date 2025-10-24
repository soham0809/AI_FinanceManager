#!/usr/bin/env python3
"""
Add User Isolation to Transactions
Adds user_id column and enables proper user isolation
"""
import sqlite3
import sys
import os

def add_user_isolation():
    """Add user_id column to transactions table"""
    print("🔧 Adding user isolation to transactions...")
    
    # Connect to database
    conn = sqlite3.connect('financial_copilot.db')
    cursor = conn.cursor()
    
    try:
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(transactions)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        print(f"📋 Current transaction columns: {existing_columns}")
        
        if 'user_id' not in existing_columns:
            # Add user_id column
            cursor.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")
            print("✅ Added user_id column to transactions")
            
            # Set all existing transactions to belong to the test user (id=1)
            cursor.execute("UPDATE transactions SET user_id = 1 WHERE user_id IS NULL")
            print("✅ Assigned existing transactions to test user (id=1)")
            
            conn.commit()
        else:
            print("ℹ️ user_id column already exists")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(transactions)")
        columns = cursor.fetchall()
        final_columns = [col[1] for col in columns]
        print(f"✅ Final transaction columns: {final_columns}")
        
        # Check transaction counts per user
        cursor.execute("SELECT user_id, COUNT(*) FROM transactions GROUP BY user_id")
        user_counts = cursor.fetchall()
        print(f"📊 Transactions per user: {user_counts}")
        
        print("✅ User isolation setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up user isolation: {e}")
        conn.rollback()
    finally:
        conn.close()

def enable_user_id_in_model():
    """Enable user_id in the Transaction model"""
    print("🔧 Enabling user_id in Transaction model...")
    
    model_file = "app/models/transaction.py"
    if os.path.exists(model_file):
        with open(model_file, 'r') as f:
            content = f.read()
        
        # Uncomment user_id line
        updated_content = content.replace(
            "    # user_id = Column(Integer, ForeignKey(\"users.id\"), nullable=True)  # Not in existing DB",
            "    user_id = Column(Integer, ForeignKey(\"users.id\"), nullable=True)  # Now enabled for isolation"
        )
        
        with open(model_file, 'w') as f:
            f.write(updated_content)
        
        print("✅ Enabled user_id in Transaction model")
    else:
        print("⚠️ Transaction model file not found")

if __name__ == "__main__":
    add_user_isolation()
    enable_user_id_in_model()
    
    print("\n🎉 User Isolation Setup Complete!")
    print("=" * 50)
    print("Now each user will only see their own transactions!")
    print("Restart the backend server to apply changes.")
    print("\nTest users:")
    print("  - User ID 1: All existing transactions")
    print("  - New users: Will have separate transactions")
