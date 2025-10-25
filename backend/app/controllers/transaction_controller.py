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
from app.utils.intelligent_sms_filter import IntelligentSMSFilter, SMSType

class TransactionController:
    def __init__(self):
        self.sms_parser = SMSParser()
        self.ai_assistant = OllamaAssistant()
        self.deduplicator = TransactionDeduplicator()
        self.intelligent_filter = IntelligentSMSFilter()
    
    async def parse_sms(self, db: Session, sms_text: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Parse SMS and create transaction using intelligent filtering and advanced classification"""
        try:
            # STEP 1: Intelligent pre-filtering to identify real transactions
            sms_type, confidence, reason = self.intelligent_filter.classify_sms(sms_text)
            
            # Only process if it's a real transaction with high confidence
            if sms_type != SMSType.REAL_TRANSACTION or confidence < 0.6:
                raise ValueError(f"SMS filtered out: {sms_type.value} (confidence: {confidence:.2f}) - {reason}")
            
            # STEP 2: Use advanced SMS classification and parsing for real transactions
            parsed_result = await classify_and_parse_sms(sms_text)
            
            if parsed_result.get('success') is False:
                raise ValueError(f"SMS parsing failed: {parsed_result.get('error', 'Unknown error')}")
            
            # Extract transaction data
            vendor = parsed_result.get('vendor', 'Unknown')
            amount = float(parsed_result.get('amount', 0))
            transaction_type = parsed_result.get('transaction_type', 'debit')
            # Map merchant_category to category for backward compatibility
            category = parsed_result.get('merchant_category', parsed_result.get('category', 'Others'))
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
                category=category,
                sms_text=sms_text,
                confidence=confidence,
                parsed_data=parsed_result,
                user_id=user_id
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
                            category=transaction_data.get('category', 'Others'),
                            sms_text=sms_text,
                            confidence=float(transaction_data.get('confidence', 0.0)),
                            user_id=user_id
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
    
    def parse_sms_local_quick(
        self,
        db: Session,
        sms_text: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fast local-only SMS parse using regex-based SMSParser; no LLM"""
        try:
            parsed = self.sms_parser.parse_transaction(sms_text)
            if not parsed.get('success'):
                raise HTTPException(status_code=400, detail=parsed.get('error', 'Failed to parse SMS'))
            vendor = parsed.get('vendor', 'Unknown')
            amount = float(parsed.get('amount', 0) or 0)
            category = parsed.get('category', 'Others')
            date_str = parsed.get('date') or datetime.now().strftime('%Y-%m-%d')
            confidence = float(parsed.get('confidence', 0.8))
            transaction = self.create_transaction(
                db=db,
                vendor=vendor,
                amount=amount,
                date=date_str,
                category=category,
                sms_text=sms_text,
                confidence=confidence,
                user_id=user_id
            )
            return {
                'success': True,
                'transaction': transaction,
                'method': 'local_quick'
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Local quick parse failed: {str(e)}")
    
    def create_enhanced_transaction(
        self,
        db: Session,
        vendor: str,
        amount: float,
        date: str,
        category: str,
        sms_text: str,
        confidence: float = 0.0,
        parsed_data: Dict[str, Any] = None,
        user_id: Optional[int] = None
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
                date=date,  # Store as string to match existing DB
                category=category,
                sms_text=sms_text,
                confidence=confidence,
                created_at=datetime.now(),
                user_id=user_id,  # Add user isolation
                # Enhanced fields from classification
                payment_method=parsed_data.get('payment_method') if parsed_data else None,
                is_subscription=parsed_data.get('is_subscription', False) if parsed_data else False,
                subscription_service=parsed_data.get('subscription_service') if parsed_data else None,
                card_last_four=parsed_data.get('card_last_four') if parsed_data else None,
                upi_transaction_id=parsed_data.get('upi_transaction_id') if parsed_data else None,
                merchant_category=parsed_data.get('merchant_category') if parsed_data else None,
                is_recurring=parsed_data.get('is_recurring', False) if parsed_data else False
            )
            
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
        category: str,
        sms_text: str,
        confidence: float = 0.0,
        user_id: Optional[int] = None
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
                date=date,  # Store as string to match existing DB
                category=category,
                sms_text=sms_text,
                confidence=confidence,
                created_at=datetime.now(),
                user_id=user_id
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            return transaction
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")
    
    def get_user_transactions(self, db: Session, user_id: int, limit: Optional[int] = None) -> List[Transaction]:
        """Get transactions for a specific user"""
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        if limit:
            query = query.limit(limit)
        return query.order_by(Transaction.date.desc()).all()
    
    def get_user_transaction_count(self, db: Session, user_id: int) -> int:
        """Get transaction count for a specific user"""
        return db.query(Transaction).filter(Transaction.user_id == user_id).count()
    
    def get_transactions(
        self,
        db: Session,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get transactions with optional user filtering"""
        query = db.query(Transaction)
        
        # Enable user filtering for proper isolation
        if user_id is not None:
            query = query.filter(Transaction.user_id == user_id)
        
        return query.order_by(Transaction.id.desc()).offset(offset).limit(limit).all()
    
    def get_transaction_by_id(self, db: Session, transaction_id: int, user_id: Optional[int] = None) -> Transaction:
        """Get transaction by ID"""
        query = db.query(Transaction).filter(Transaction.id == transaction_id)
        
        # Enable user filtering for proper isolation
        if user_id is not None:
            query = query.filter(Transaction.user_id == user_id)
        
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
