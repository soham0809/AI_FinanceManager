"""
Pytest Configuration and Fixtures
Shared test infrastructure for all test modules
"""
import pytest
import sys
import os
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config.database import Base, get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.controllers.auth_controller import AuthController

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Create a fresh database for each test"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    db = TestSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """Create a test client with database dependency override"""
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db: Session) -> User:
    """Create a test user"""
    user = AuthController.create_user(
        db=test_db,
        email="test@example.com",
        username="testuser",
        password="testpassword123",
        full_name="Test User"
    )
    return user


@pytest.fixture(scope="function")
def auth_headers(test_db: Session, test_user: User) -> Dict[str, str]:
    """Create authentication headers for test user"""
    token_data = AuthController.create_access_token_for_user(test_user, test_db)
    return {
        "Authorization": f"Bearer {token_data['access_token']}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def another_user(test_db: Session) -> User:
    """Create another test user for multi-user tests"""
    user = AuthController.create_user(
        db=test_db,
        email="another@example.com",
        username="anotheruser",
        password="password123",
        full_name="Another User"
    )
    return user


@pytest.fixture(scope="function")
def sample_transactions(test_db: Session, test_user: User):
    """Create sample transactions for testing"""
    from datetime import datetime, timedelta
    
    transactions = []
    base_date = datetime.now()
    
    # Create diverse transactions
    test_data = [
        ("Amazon", 500.0, "Shopping", "debit", 0.95),
        ("Swiggy", 350.0, "Food & Dining", "debit", 0.90),
        ("Salary Credit", 50000.0, "Salary", "credit", 1.0),
        ("Netflix", 199.0, "Entertainment", "debit", 0.92),
        ("Uber", 250.0, "Transportation", "debit", 0.88),
        ("Flipkart", 1200.0, "Shopping", "debit", 0.93),
        ("Zomato", 450.0, "Food & Dining", "debit", 0.91),
        ("HDFC Bank", 5000.0, "Transfer", "credit", 0.95),
    ]
    
    for i, (vendor, amount, category, tx_type, confidence) in enumerate(test_data):
        transaction = Transaction(
            user_id=test_user.id,
            vendor=vendor,
            amount=amount,
            category=category,
            transaction_type=tx_type,
            confidence=confidence,
            date=base_date - timedelta(days=i),
            sms_text=f"Test SMS for {vendor}"
        )
        test_db.add(transaction)
        transactions.append(transaction)
    
    test_db.commit()
    
    for tx in transactions:
        test_db.refresh(tx)
    
    return transactions


@pytest.fixture(scope="function")
def sample_sms_messages():
    """Sample SMS messages for testing"""
    return [
        "Your account XXXXXXX1234 has been debited by Rs.500.00 at AMAZON on 25-Dec-24. Available balance: Rs.5000",
        "INR 350.00 debited from A/c XX1234 on 24-DEC-24 to VPA swiggy@paytm. UPI Ref No 123456789",
        "Rs 50000.00 credited to your account XX1234 on 23-Dec-24. Salary for Dec 2024.",
        "Your A/c XX1234 debited Rs.199.00 for NETFLIX on 22-Dec-24. Avl bal: Rs.10000",
        "Payment of Rs.250 made to UBER using card XX1234 on 21-Dec-24",
    ]
