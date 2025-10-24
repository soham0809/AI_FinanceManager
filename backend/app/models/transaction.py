"""Transaction model"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Now enabled for isolation
    sms_text = Column(Text, nullable=True)  # Matches existing DB
    vendor = Column(Text, nullable=True)  # Matches existing DB (TEXT, nullable)
    amount = Column(Float, nullable=True)  # Matches existing DB (REAL, nullable)
    date = Column(Text, nullable=True)  # Matches existing DB (TEXT, nullable)
    # transaction_type = Column(String(50), nullable=False)  # Not in existing DB
    category = Column(Text, nullable=True)  # Matches existing DB (TEXT, nullable)
    # success = Column(Boolean, default=True)  # Not in existing DB
    # raw_text = Column(Text, nullable=True)  # Not in existing DB (using sms_text instead)
    confidence = Column(Float, nullable=True)  # Matches existing DB (REAL, nullable)
    # transaction_id = Column(String(255), nullable=True)  # UPI ref, etc. - Not in existing DB
    created_at = Column(DateTime, nullable=True)  # Matches existing DB (TIMESTAMP, nullable)
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Not in existing DB
    
    # New fields for enhanced transaction classification (these exist in DB)
    payment_method = Column(String(50), nullable=True)  # 'UPI', 'Credit Card', 'Debit Card', 'Net Banking', etc.
    is_subscription = Column(Boolean, nullable=True)
    subscription_service = Column(String(100), nullable=True)  # 'Netflix', 'Amazon Prime', 'Spotify', etc.
    card_last_four = Column(String(4), nullable=True)  # Last 4 digits of card
    upi_transaction_id = Column(String(255), nullable=True)  # UPI reference number
    merchant_category = Column(String(100), nullable=True)  # Detailed merchant category
    is_recurring = Column(Boolean, nullable=True)  # Whether this is a recurring payment
    
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
