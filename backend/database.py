from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
from typing import List, Optional

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///financial_copilot.db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'debit' or 'credit'
    category = Column(String(100), nullable=True)
    success = Column(Boolean, default=True)
    raw_text = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    color = Column(String(7), default="#2196F3")  # Hex color code
    icon = Column(String(50), default="category")
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database operations
class DatabaseManager:
    def __init__(self):
        create_tables()
        self._seed_categories()
    
    def _seed_categories(self):
        """Seed default categories"""
        db = SessionLocal()
        try:
            # Check if categories already exist
            if db.query(Category).count() > 0:
                return
            
            default_categories = [
                {"name": "Food & Dining", "description": "Restaurants, food delivery, groceries", "color": "#FF9800", "icon": "restaurant"},
                {"name": "Shopping", "description": "Online shopping, retail, clothing", "color": "#E91E63", "icon": "shopping_bag"},
                {"name": "Transportation", "description": "Uber, Ola, fuel, public transport", "color": "#2196F3", "icon": "directions_car"},
                {"name": "Entertainment", "description": "Movies, streaming, games", "color": "#9C27B0", "icon": "movie"},
                {"name": "Healthcare", "description": "Medical, pharmacy, hospital", "color": "#4CAF50", "icon": "local_hospital"},
                {"name": "Education", "description": "Courses, books, training", "color": "#FF5722", "icon": "school"},
                {"name": "Utilities", "description": "Bills, electricity, internet, mobile", "color": "#607D8B", "icon": "flash_on"},
                {"name": "Fuel", "description": "Petrol, diesel, gas", "color": "#795548", "icon": "local_gas_station"},
                {"name": "Financial", "description": "Banking, investments, transfers", "color": "#009688", "icon": "account_balance"},
                {"name": "Others", "description": "Miscellaneous expenses", "color": "#9E9E9E", "icon": "category"},
            ]
            
            for cat_data in default_categories:
                category = Category(**cat_data)
                db.add(category)
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error seeding categories: {e}")
        finally:
            db.close()
    
    def add_transaction(self, transaction_data: dict) -> Transaction:
        """Add a new transaction to the database"""
        db = SessionLocal()
        try:
            # Parse date string to datetime
            if isinstance(transaction_data.get('date'), str):
                transaction_data['date'] = datetime.fromisoformat(transaction_data['date'].replace('Z', '+00:00'))
            
            transaction = Transaction(**transaction_data)
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            return transaction
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to add transaction: {e}")
        finally:
            db.close()
    
    def get_transactions(self, limit: int = 100, offset: int = 0) -> List[Transaction]:
        """Get transactions with pagination"""
        db = SessionLocal()
        try:
            transactions = db.query(Transaction)\
                           .order_by(Transaction.date.desc())\
                           .offset(offset)\
                           .limit(limit)\
                           .all()
            return transactions
        finally:
            db.close()
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a specific transaction by ID"""
        db = SessionLocal()
        try:
            return db.query(Transaction).filter(Transaction.id == transaction_id).first()
        finally:
            db.close()
    
    def update_transaction(self, transaction_id: int, update_data: dict) -> Optional[Transaction]:
        """Update a transaction"""
        db = SessionLocal()
        try:
            transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if transaction:
                for key, value in update_data.items():
                    setattr(transaction, key, value)
                transaction.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(transaction)
            return transaction
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to update transaction: {e}")
        finally:
            db.close()
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        db = SessionLocal()
        try:
            transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if transaction:
                db.delete(transaction)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete transaction: {e}")
        finally:
            db.close()
    
    def get_transaction_stats(self) -> dict:
        """Get transaction statistics"""
        db = SessionLocal()
        try:
            total_transactions = db.query(Transaction).count()
            total_debits = db.query(Transaction).filter(Transaction.transaction_type == 'debit').count()
            total_credits = db.query(Transaction).filter(Transaction.transaction_type == 'credit').count()
            
            # Calculate totals
            debit_sum = db.query(Transaction)\
                         .filter(Transaction.transaction_type == 'debit')\
                         .with_entities(Transaction.amount)\
                         .all()
            total_spent = sum([t.amount for t in debit_sum]) if debit_sum else 0.0
            
            credit_sum = db.query(Transaction)\
                          .filter(Transaction.transaction_type == 'credit')\
                          .with_entities(Transaction.amount)\
                          .all()
            total_received = sum([t.amount for t in credit_sum]) if credit_sum else 0.0
            
            # Category breakdown
            category_stats = db.query(Transaction.category, Transaction.amount)\
                              .filter(Transaction.transaction_type == 'debit')\
                              .all()
            
            category_breakdown = {}
            for category, amount in category_stats:
                cat_name = category or 'Uncategorized'
                category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + amount
            
            return {
                'total_transactions': total_transactions,
                'total_debits': total_debits,
                'total_credits': total_credits,
                'total_spent': total_spent,
                'total_received': total_received,
                'net_balance': total_received - total_spent,
                'category_breakdown': category_breakdown
            }
        finally:
            db.close()
    
    def get_categories(self) -> List[Category]:
        """Get all categories"""
        db = SessionLocal()
        try:
            return db.query(Category).all()
        except Exception as e:
            raise Exception(f"Failed to get categories: {e}")
    
    def search_transactions(self, query: str, limit: int = 50):
        """Search transactions by vendor or category"""
        db = SessionLocal()
        try:
            return db.query(Transaction).filter(
                or_(
                    Transaction.vendor.ilike(f"%{query}%"),
                    Transaction.category.ilike(f"%{query}%")
                )
            ).order_by(Transaction.date.desc()).limit(limit).all()
        finally:
            db.close()
    
    def get_all_transactions(self, db: Session):
        """Get all transactions for analysis"""
        return db.query(Transaction).order_by(Transaction.date.desc()).all()
    
    def get_spending_by_category(self, db: Session):
        """Get spending breakdown by category"""
        from sqlalchemy import func
        
        result = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            Transaction.transaction_type == 'debit'
        ).group_by(Transaction.category).all()
        
        return [(category, float(total_amount)) for category, total_amount in result]
    
    def get_monthly_spending_trends(self, db: Session):
        """Get monthly spending trends"""
        from sqlalchemy import func
        
        # Use strftime for SQLite compatibility
        result = db.query(
            func.strftime('%Y', Transaction.date).label('year'),
            func.strftime('%m', Transaction.date).label('month'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            Transaction.transaction_type == 'debit'
        ).group_by(
            func.strftime('%Y', Transaction.date),
            func.strftime('%m', Transaction.date)
        ).order_by('year', 'month').all()
        
        monthly_data = []
        for year, month, total_amount in result:
            if year and month and total_amount:
                monthly_data.append({
                    'year': int(year),
                    'month': int(month),
                    'month_name': [
                        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                    ][int(month) - 1],
                    'total_spending': float(total_amount)
                })
        
        return monthly_data
    
    def get_spending_insights(self, db: Session):
        """Get comprehensive spending insights"""
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Basic stats
        total_transactions = db.query(Transaction).count()
        total_spending = db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'debit'
        ).scalar() or 0
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'credit'
        ).scalar() or 0
        
        # Average transaction amount
        avg_transaction = db.query(func.avg(Transaction.amount)).filter(
            Transaction.transaction_type == 'debit'
        ).scalar() or 0
        
        # Most frequent category
        most_frequent_category = db.query(
            Transaction.category,
            func.count(Transaction.id).label('count')
        ).filter(
            Transaction.transaction_type == 'debit'
        ).group_by(Transaction.category).order_by(func.count(Transaction.id).desc()).first()
        
        # Highest spending category
        highest_spending_category = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.transaction_type == 'debit'
        ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).first()
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_spending = db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'debit',
            Transaction.date >= week_ago
        ).scalar() or 0
        
        return {
            'total_transactions': total_transactions,
            'total_spending': float(total_spending),
            'total_income': float(total_income),
            'net_balance': float(total_income - total_spending),
            'average_transaction': float(avg_transaction),
            'most_frequent_category': most_frequent_category[0] if most_frequent_category else 'N/A',
            'highest_spending_category': highest_spending_category[0] if highest_spending_category else 'N/A',
            'recent_spending_7days': float(recent_spending)
        }
    
    def get_top_vendors(self, db: Session, limit: int = 10):
        """Get top spending vendors"""
        from sqlalchemy import func
        
        result = db.query(
            Transaction.vendor,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            Transaction.transaction_type == 'debit'
        ).group_by(Transaction.vendor).order_by(
            func.sum(Transaction.amount).desc()
        ).limit(limit).all()
        
        return [
            {
                'vendor': vendor,
                'total_spending': float(total_amount),
                'transaction_count': transaction_count
            }
            for vendor, total_amount, transaction_count in result
        ]

# Global database manager instance
db_manager = DatabaseManager()
