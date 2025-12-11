"""
Simple authentication setup script
Run this to set up the database for authentication
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.database import engine, Base
from app.models.user import User
from app.models.transaction import Transaction

def main():
    print("🔄 Setting up authentication system...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test database connection
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check users table
        try:
            users_count = db.query(User).count()
            print(f"✅ Users table ready. Current users: {users_count}")
        except Exception as e:
            print(f"⚠️  Users table issue: {e}")
        
        # Check transactions table  
        try:
            transactions_count = db.query(Transaction).count()
            print(f"✅ Transactions table ready. Current transactions: {transactions_count}")
        except Exception as e:
            print(f"⚠️  Transactions table issue: {e}")
        
        db.close()
        
        print("\n🎉 Authentication system setup completed!")
        print("\n📋 Next steps:")
        print("1. Start the backend server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("2. Test authentication endpoints at: http://192.168.0.102:8000/docs")
        print("3. Use the Flutter app to register and login")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("- Make sure you're in the backend directory")
        print("- Check if the database file exists")
        print("- Verify all dependencies are installed")

if __name__ == "__main__":
    main()
