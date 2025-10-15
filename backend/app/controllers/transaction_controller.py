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
from app.utils.sms_classifier import classify_and_parse_sms

class TransactionController:
    def __init__(self):
        self.sms_parser = SMSParser()
        self.ai_assistant = OllamaAssistant()
        self.deduplicator = TransactionDeduplicator()
    
    async def parse_sms(self, db: Session, sms_text: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Parse SMS and create transaction using advanced classification"""
        try:
            # Use new advanced SMS classification and parsing
            parsed_result = await classify_and_parse_sms(sms_text)
            
            if parsed_result.get('success') is False:
                raise ValueError(f"SMS parsing failed: {parsed_result.get('error', 'Unknown error')}")
            
            # Extract transaction data
            vendor = parsed_result.get('vendor', 'Unknown')
            amount = float(parsed_result.get('amount', 0))
            transaction_type = parsed_result.get('transaction_type', 'debit')
            category = parsed_result.get('category', 'Others')
            confidence = float(parsed_result.get('confidence', 0.0))
            
            # Format date properly if provided
            date_str = parsed_result.get('date')
            if not date_str or date_str == 'null':
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Apply confidence threshold filtering
            if confidence < 0.7:
                raise ValueError(f"Low confidence transaction ({confidence:.2f})")
            
            # Prepare transaction data for duplicate detection
            duplicate_check_data = {
                'vendor': vendor,
                'amount': amount,
                'date': date_str,
                'transaction_type': transaction_type,
                'category': category,
                'transaction_id': parsed_result.get('upi_transaction_id')
            }
            
            # Check for duplicates
            duplicate_result = self.deduplicator.is_duplicate(duplicate_check_data)
            if duplicate_result['is_duplicate']:
                raise ValueError(f"Duplicate transaction: {duplicate_result['reason']}")
            
            # Create transaction with enhanced data
            transaction = self.create_enhanced_transaction(
                db=db,
                vendor=vendor,
                amount=amount,
                date=date_str,
                transaction_type=transaction_type,
                category=category,
                raw_text=sms_text,
                confidence=confidence,
                parsed_data=parsed_result
            )
            
            # Add to deduplicator
            self.deduplicator.add_transaction(duplicate_check_data)
            
            return {
                'success': True,
                'transaction': transaction,
                'method': 'advanced_classifier',
                'classification': parsed_result.get('payment_method', 'Unknown')
            }
                
        except ValueError as e:
            # Fallback to old parsing method if new method fails
            try:
                if self.ai_assistant.initialized:
                    ai_result = self.ai_assistant.parse_sms_transaction(sms_text)
                    
                    if ai_result['success']:
                        transaction_data = ai_result['transaction_data']
                        
                        # Format date properly if provided
                        if transaction_data.get('date') and transaction_data['date'] != 'null':
                            date_str = self.sms_parser.format_date(transaction_data['date'])
                        else:
                            date_str = datetime.now().strftime('%Y-%m-%d')
                        
                        # Create transaction with old method
                        transaction = self.create_transaction(
                            db=db,
                            vendor=transaction_data.get('vendor', 'Unknown'),
                            amount=float(transaction_data['amount']),
                            date=date_str,
                            transaction_type=transaction_data.get('transaction_type', 'debit'),
                            category=transaction_data.get('category', 'Others'),
                            raw_text=sms_text,
                            confidence=float(transaction_data.get('confidence', 0.0))
                        )
                        
                        return {
                            'success': True,
                            'transaction': transaction,
                            'method': 'fallback_ollama'
                        }
                
                raise HTTPException(status_code=400, detail=str(e))
            except Exception:
                raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    def create_enhanced_transaction(
        self,
        db: Session,
        vendor: str,
        amount: float,
        date: str,
        transaction_type: str,
        category: str,
        raw_text: str,
        confidence: float = 0.0,
        parsed_data: Dict[str, Any] = None
    ) -> Transaction:
        """Create a new transaction with enhanced classification data"""
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
            
            # Create transaction with enhanced fields
            transaction = Transaction(
                vendor=vendor,
                amount=amount,
                date=transaction_date,
                transaction_type=transaction_type,
                category=category,
                raw_text=raw_text,
                confidence=confidence,
                # Enhanced fields from classification
                payment_method=parsed_data.get('payment_method') if parsed_data else None,
                is_subscription=parsed_data.get('is_subscription', False) if parsed_data else False,
                subscription_service=parsed_data.get('subscription_service') if parsed_data else None,
                card_last_four=parsed_data.get('card_last_four') if parsed_data else None,
                upi_transaction_id=parsed_data.get('upi_transaction_id') if parsed_data else None,
                merchant_category=parsed_data.get('merchant_category') if parsed_data else None,
                is_recurring=parsed_data.get('is_recurring', False) if parsed_data else False
            )
            transaction.success = True
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            return transaction
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create enhanced transaction: {str(e)}")
    
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
