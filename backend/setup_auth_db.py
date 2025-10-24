"""
Simple database setup script for authentication system
This script will create the users table with refresh token support
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config.database import Base, engine
from app.models.user import User
from app.models.transaction import Transaction

def setup_database():
    """Setup database with authentication tables"""
    print("🔄 Setting up authentication database...")
    
    try:
        # Create all tables (this will add new columns if they don't exist)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/updated successfully!")
        
        # Create a session to test the connection
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Test if we can query the users table
        users_count = db.query(User).count()
        print(f"✅ Users table accessible. Current user count: {users_count}")
        
        # Test if we can query the transactions table
        transactions_count = db.query(Transaction).count()
        print(f"✅ Transactions table accessible. Current transaction count: {transactions_count}")
        
        db.close()
        
        print("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == "__main__":
    setup_database()
