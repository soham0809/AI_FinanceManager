#!/usr/bin/env python3
"""
Fix Users Table for Authentication
Adds missing columns to existing users table
"""
import sqlite3
import sys
import os

def fix_users_table():
    """Fix the users table by adding missing columns"""
    print("🔧 Fixing users table for authentication...")
    
    # Connect to database
    conn = sqlite3.connect('financial_copilot.db')
    cursor = conn.cursor()
    
    try:
        # Check current table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]
        print(f"📋 Current columns: {existing_columns}")
        
        # Add missing columns
        required_columns = {
            'hashed_password': 'VARCHAR(255) NOT NULL DEFAULT ""',
            'full_name': 'VARCHAR(255)',
            'is_active': 'BOOLEAN DEFAULT TRUE',
            'is_verified': 'BOOLEAN DEFAULT FALSE',
            'refresh_token': 'TEXT',
            'refresh_token_expires_at': 'DATETIME',
            'updated_at': 'DATETIME'
        }
        
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Column {column_name} might already exist: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify final structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        final_columns = [col[1] for col in columns]
        print(f"✅ Final columns: {final_columns}")
        
        print("✅ Users table fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing users table: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_test_user():
    """Create a test user using direct SQL"""
    print("👤 Creating test user with SQL...")
    
    conn = sqlite3.connect('financial_copilot.db')
    cursor = conn.cursor()
    
    try:
        # Check if test user exists
        cursor.execute("SELECT * FROM users WHERE username = ?", ("testuser",))
        if cursor.fetchone():
            print("ℹ️ Test user already exists")
            return
        
        # Hash password manually (simple hash for testing)
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("testpass123")
        
        # Insert test user
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, full_name, is_active, is_verified, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, ("testuser", "test@example.com", hashed_password, "Test User", True, False))
        
        conn.commit()
        print("✅ Test user created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_users_table()
    create_test_user()
    
    print("\n🎉 Database Fix Complete!")
    print("=" * 50)
    print("Test credentials:")
    print("  Username: testuser")
    print("  Password: testpass123")
    print("  Email: test@example.com")
    print("\nAuthentication should now work!")
