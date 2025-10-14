"""Transaction controller for business logic"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.transaction import Transaction, Category
from app.models.user import User
from app.utils.sms_parser import SMSParser
from app.utils.ollama_integration import OllamaAssistant
from app.utils.transaction_deduplicator import TransactionDeduplicator

class TransactionController:
    def __init__(self):
        self.sms_parser = SMSParser()
        self.ai_assistant = OllamaAssistant()
        self.deduplicator = TransactionDeduplicator()
    
    def parse_sms(self, db: Session, sms_text: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Parse SMS and create transaction"""
        try:
            # First try Ollama AI parsing
            if self.ai_assistant.initialized:
                ai_result = self.ai_assistant.parse_sms_transaction(sms_text)
                
                if ai_result['success']:
                    transaction_data = ai_result['transaction_data']
                    
                    # Format date properly if provided
                    if transaction_data.get('date') and transaction_data['date'] != 'null':
                        date_str = self.sms_parser.format_date(transaction_data['date'])
                    else:
                        date_str = datetime.now().strftime('%Y-%m-%d')
                    
                    # Prepare transaction data for duplicate detection
                    duplicate_check_data = {
                        'vendor': transaction_data.get('vendor', 'Unknown'),
                        'amount': float(transaction_data['amount']),
                        'date': date_str,
                        'transaction_type': transaction_data.get('transaction_type', 'debit'),
                        'category': transaction_data.get('category', 'Others'),
                        'transaction_id': transaction_data.get('transaction_id')
                    }
                    
                    # Apply confidence threshold filtering
                    confidence_score = float(transaction_data.get('confidence', 0.0))
                    if confidence_score < 0.7:
                        raise ValueError(f"Low confidence transaction ({confidence_score:.2f})")
                    
                    # Check for duplicates
                    duplicate_result = self.deduplicator.is_duplicate(duplicate_check_data)
                    if duplicate_result['is_duplicate']:
                        raise ValueError(f"Duplicate transaction: {duplicate_result['reason']}")
                    
                    # Create transaction
                    transaction = self.create_transaction(
                        db=db,
                        vendor=duplicate_check_data['vendor'],
                        amount=duplicate_check_data['amount'],
                        date=date_str,
                        transaction_type=duplicate_check_data['transaction_type'],
                        category=duplicate_check_data['category'],
                        raw_text=sms_text,
                        confidence=confidence_score
                    )
                    
                    # Add to deduplicator
                    self.deduplicator.add_transaction(duplicate_check_data)
                    
                    return {
                        'success': True,
                        'transaction': transaction,
                        'method': 'ollama_ai'
                    }
                else:
                    # Check if rejected as promotional
                    if ai_result.get('is_promotional'):
                        raise ValueError(f"Promotional message: {ai_result.get('error')}")
            
            # Fallback to regex parsing
            parsed_result = self.sms_parser.parse_transaction(sms_text)
            
            if parsed_result['success']:
                transaction = self.create_transaction(
                    db=db,
                    vendor=parsed_result['vendor'],
                    amount=parsed_result['amount'],
                    date=parsed_result['date'],
                    transaction_type=parsed_result['transaction_type'],
                    category=parsed_result['category'],
                    raw_text=sms_text,
                    confidence=parsed_result['confidence']
                )
                
                return {
                    'success': True,
                    'transaction': transaction,
                    'method': 'regex_parser'
                }
            else:
                raise ValueError("Could not parse transaction data from SMS")
                
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    def create_transaction(
        self,
        db: Session,
        vendor: str,
        amount: float,
        date: str,
        transaction_type: str,
        category: str,
        raw_text: str,
        confidence: float = 0.0
    ) -> Transaction:
        """Create a new transaction"""
        try:
            # Parse date string to datetime with flexible format handling
            if isinstance(date, str):
                try:
                    # Try ISO format first (from mobile app)
                    if 'T' in date:
                        # Remove microseconds if present
                        date_clean = date.split('.')[0] if '.' in date else date
                        transaction_date = datetime.fromisoformat(date_clean.replace('T', ' '))
                    else:
                        # Try standard date format
                        transaction_date = datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    # Fallback to current date if parsing fails
                    transaction_date = datetime.now()
            else:
                transaction_date = date
            
            # Validate date - if it's in the future, adjust it to current year
            current_year = datetime.now().year
            if transaction_date.year > current_year:
                # If year is 2026 or later, assume it should be current year
                transaction_date = transaction_date.replace(year=current_year)
            
            transaction = Transaction(
                vendor=vendor,
                amount=amount,
                date=transaction_date,
                transaction_type=transaction_type,
                category=category,
                raw_text=raw_text,
                confidence=confidence
            )
            transaction.success = True
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            return transaction
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")
    
    def get_transactions(
        self,
        db: Session,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get transactions with optional user filtering"""
        query = db.query(Transaction)
        
        # User filtering disabled for backward compatibility
        # if user_id:
        #     query = query.filter(Transaction.user_id == user_id)
        
        return query.order_by(Transaction.date.desc()).offset(offset).limit(limit).all()
    
    def get_transaction_by_id(self, db: Session, transaction_id: int, user_id: Optional[int] = None) -> Transaction:
        """Get transaction by ID"""
        query = db.query(Transaction).filter(Transaction.id == transaction_id)
        
        # User filtering disabled for backward compatibility
        # if user_id:
        #     query = query.filter(Transaction.user_id == user_id)
        
        transaction = query.first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return transaction
    
    def update_transaction(
        self,
        db: Session,
        transaction_id: int,
        user_id: Optional[int] = None,
        **kwargs
    ) -> Transaction:
        """Update transaction"""
        transaction = self.get_transaction_by_id(db, transaction_id, user_id)
        
        for key, value in kwargs.items():
            if hasattr(transaction, key) and value is not None:
                setattr(transaction, key, value)
        
        db.commit()
        db.refresh(transaction)
        return transaction
    
    def delete_transaction(self, db: Session, transaction_id: int, user_id: Optional[int] = None):
        """Delete transaction"""
        transaction = self.get_transaction_by_id(db, transaction_id, user_id)
        db.delete(transaction)
        db.commit()
        return {"message": "Transaction deleted successfully"}
    
    def search_transactions(
        self,
        db: Session,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Transaction]:
        """Search transactions by vendor or category"""
        from sqlalchemy import or_
        
        search_query = db.query(Transaction).filter(
            or_(
                Transaction.vendor.ilike(f"%{query}%"),
                Transaction.category.ilike(f"%{query}%")
            )
        )
        
        # User filtering disabled for backward compatibility
        # if user_id:
        #     search_query = search_query.filter(Transaction.user_id == user_id)
        
        return search_query.order_by(Transaction.date.desc()).limit(limit).all()
    
    def get_categories(self, db: Session) -> List[Category]:
        """Get all categories"""
        return db.query(Category).all()
    
    def create_category(self, db: Session, name: str, description: str = None, color: str = None, icon: str = None) -> Category:
        """Create new category"""
        category = Category(
            name=name,
            description=description,
            color=color,
            icon=icon
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
