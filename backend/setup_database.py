#!/usr/bin/env python3
"""
Setup Database for AI Finance Manager
Creates all necessary tables including users table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.database import engine, Base
from app.models.user import User
from app.models.transaction import Transaction
from sqlalchemy import text
import sqlite3

def setup_database():
    """Setup database with all required tables"""
    print("🗄️ Setting up AI Finance Manager Database...")
    
    # Create all tables
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Check if tables were created
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        print(f"✅ Created tables: {tables}")
    
    # Check users table structure
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = result.fetchall()
            print(f"👤 Users table columns: {[col[1] for col in columns]}")
    except Exception as e:
        print(f"⚠️ Users table check failed: {e}")
    
    # Check transactions table structure
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(transactions)"))
            columns = result.fetchall()
            print(f"💳 Transactions table columns: {[col[1] for col in columns]}")
    except Exception as e:
        print(f"⚠️ Transactions table check failed: {e}")
    
    print("✅ Database setup complete!")

def create_test_user():
    """Create a test user for authentication testing"""
    from app.config.database import get_db
    from app.controllers.auth_controller import AuthController
    
    print("👤 Creating test user...")
    
    db = next(get_db())
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            print("ℹ️ Test user already exists")
            return
        
        # Create test user
        user = AuthController.create_user(
            db=db,
            email="test@example.com",
            username="testuser",
            password="testpass123",
            full_name="Test User"
        )
        print(f"✅ Created test user: {user.username} ({user.email})")
        
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
    create_test_user()
    
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("Test credentials:")
    print("  Username: testuser")
    print("  Password: testpass123")
    print("  Email: test@example.com")
    print("\nYou can now test the authentication system!")
