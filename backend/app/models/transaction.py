"""Transaction model"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User isolation
    sms_text = Column(Text, nullable=True)  # Original SMS text
    vendor = Column(Text, nullable=True)  # Merchant/vendor name
    amount = Column(Float, nullable=True)  # Transaction amount (always positive)
    date = Column(DateTime, nullable=True)  # Transaction date (now DateTime for proper queries)
    transaction_type = Column(String(50), nullable=True, default='debit')  # 'debit' or 'credit' - REQUIRED FIX
    category = Column(Text, nullable=True)  # Spending category
    confidence = Column(Float, nullable=True)  # Parsing confidence score
    created_at = Column(DateTime, nullable=True, default=func.now())  # Record creation timestamp
    
    # NEW: Temporal-Context Aware Parsing fields
    fingerprint = Column(String(64), unique=True, index=True, nullable=True)  # MD5 hash for fast dedup
    device_received_at = Column(DateTime, nullable=True)  # When SMS was received on device
    sender_address = Column(String(100), nullable=True)  # SMS sender (bank ID)
    
    # Enhanced transaction classification fields
    payment_method = Column(String(50), nullable=True)  # 'UPI', 'Credit Card', 'Debit Card', 'Net Banking', etc.
    is_subscription = Column(Boolean, nullable=True, default=False)
    subscription_service = Column(String(100), nullable=True)  # 'Netflix', 'Amazon Prime', 'Spotify', etc.
    card_last_four = Column(String(4), nullable=True)  # Last 4 digits of card
    upi_transaction_id = Column(String(255), nullable=True)  # UPI reference number
    merchant_category = Column(String(100), nullable=True)  # Detailed merchant category
    is_recurring = Column(Boolean, nullable=True, default=False)  # Whether this is a recurring payment
    
    # Composite index for fingerprint lookup
    __table_args__ = (
        Index('idx_fingerprint_user', 'fingerprint', 'user_id'),
    )
    
    # Relationship disabled for backward compatibility
    # user = relationship("User", back_populates="transactions", lazy="select")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, vendor={self.vendor}, amount={self.amount})>"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"
