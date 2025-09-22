"""
Data validation and sanitization module for robust transaction processing
"""
import re
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Handles data validation, sanitization, and outlier detection"""
    
    # Valid transaction types
    VALID_TRANSACTION_TYPES = ['debit', 'credit']
    
    # Valid categories (expandable)
    VALID_CATEGORIES = [
        'food', 'transport', 'shopping', 'entertainment', 'bills', 'healthcare',
        'education', 'investment', 'transfer', 'salary', 'refund', 'other'
    ]
    
    # Outlier detection thresholds
    MAX_TRANSACTION_AMOUNT = 1000000  # 10 lakh
    MIN_TRANSACTION_AMOUNT = 0.01     # 1 paisa
    
    @staticmethod
    def validate_sms_text(sms_text: str) -> Dict[str, Any]:
        """Validate and sanitize SMS text input"""
        if not sms_text or not isinstance(sms_text, str):
            return {
                'valid': False,
                'error': 'SMS text is required and must be a string',
                'sanitized_text': None
            }
        
        # Remove excessive whitespace and normalize
        sanitized = re.sub(r'\s+', ' ', sms_text.strip())
        
        # Check minimum length
        if len(sanitized) < 10:
            return {
                'valid': False,
                'error': 'SMS text too short to contain transaction information',
                'sanitized_text': sanitized
            }
        
        # Check maximum length (prevent DoS)
        if len(sanitized) > 1000:
            return {
                'valid': False,
                'error': 'SMS text too long',
                'sanitized_text': sanitized[:1000]
            }
        
        # Special handling for common bank SMS formats
        # This helps ensure proper parsing for specific bank formats
        if 'hdfc bank' in sanitized.lower() and 'debited' in sanitized.lower() and 'at ' in sanitized.lower():
            # Make sure we don't modify the SMS too much, just ensure it's parseable
            logger.info(f"Detected HDFC Bank SMS format: {sanitized}")
        
        return {
            'valid': True,
            'error': None,
            'sanitized_text': sanitized
        }
    
    @staticmethod
    def validate_amount(amount: Union[str, float, int]) -> Dict[str, Any]:
        """Validate and sanitize transaction amount"""
        try:
            # Convert to float
            if isinstance(amount, str):
                # Remove currency symbols and commas
                cleaned_amount = re.sub(r'[₹,\s]', '', amount)
                amount_float = float(cleaned_amount)
            else:
                amount_float = float(amount)
            
            # Check for negative amounts (should be handled by transaction type)
            if amount_float < 0:
                return {
                    'valid': False,
                    'error': 'Amount cannot be negative',
                    'sanitized_amount': abs(amount_float)
                }
            
            # Check minimum amount
            if amount_float < DataValidator.MIN_TRANSACTION_AMOUNT:
                return {
                    'valid': False,
                    'error': f'Amount too small (minimum: ₹{DataValidator.MIN_TRANSACTION_AMOUNT})',
                    'sanitized_amount': amount_float
                }
            
            # Check for outliers (very large amounts)
            if amount_float > DataValidator.MAX_TRANSACTION_AMOUNT:
                logger.warning(f"Large transaction detected: ₹{amount_float}")
                return {
                    'valid': True,
                    'error': None,
                    'sanitized_amount': amount_float,
                    'is_outlier': True,
                    'outlier_reason': 'Unusually large amount'
                }
            
            return {
                'valid': True,
                'error': None,
                'sanitized_amount': round(amount_float, 2),
                'is_outlier': False
            }
            
        except (ValueError, TypeError) as e:
            return {
                'valid': False,
                'error': f'Invalid amount format: {str(e)}',
                'sanitized_amount': None
            }
    
    @staticmethod
    def validate_date(date_input: Union[str, datetime]) -> Dict[str, Any]:
        """Validate and sanitize date input"""
        try:
            if isinstance(date_input, str):
                # Try multiple date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%d-%m-%Y',
                    '%d/%m/%Y',
                    '%Y-%m-%d %H:%M:%S',
                    '%d-%m-%Y %H:%M:%S'
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_input, fmt)
                        break
                    except ValueError:
                        continue
                
                if not parsed_date:
                    return {
                        'valid': False,
                        'error': 'Invalid date format',
                        'sanitized_date': None
                    }
            else:
                parsed_date = date_input
            
            # Check if date is in reasonable range
            now = datetime.now()
            min_date = now - timedelta(days=365 * 5)  # 5 years ago
            max_date = now + timedelta(days=1)  # Tomorrow
            
            if parsed_date < min_date:
                return {
                    'valid': False,
                    'error': 'Date too old (more than 5 years)',
                    'sanitized_date': parsed_date
                }
            
            if parsed_date > max_date:
                return {
                    'valid': False,
                    'error': 'Date cannot be in the future',
                    'sanitized_date': parsed_date
                }
            
            return {
                'valid': True,
                'error': None,
                'sanitized_date': parsed_date.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Date validation error: {str(e)}',
                'sanitized_date': None
            }
    
    @staticmethod
    def validate_vendor(vendor: str) -> Dict[str, Any]:
        """Validate and sanitize vendor name"""
        if not vendor or not isinstance(vendor, str):
            return {
                'valid': False,
                'error': 'Vendor name is required',
                'sanitized_vendor': 'Unknown'
            }
        
        # Clean and normalize vendor name
        sanitized = re.sub(r'[^\w\s\-\.]', '', vendor.strip().title())
        
        if len(sanitized) < 2:
            return {
                'valid': False,
                'error': 'Vendor name too short',
                'sanitized_vendor': 'Unknown'
            }
        
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return {
            'valid': True,
            'error': None,
            'sanitized_vendor': sanitized
        }
    
    @staticmethod
    def validate_transaction_type(transaction_type: str) -> Dict[str, Any]:
        """Validate transaction type"""
        if not transaction_type or not isinstance(transaction_type, str):
            return {
                'valid': False,
                'error': 'Transaction type is required',
                'sanitized_type': 'debit'
            }
        
        normalized_type = transaction_type.lower().strip()
        
        if normalized_type not in DataValidator.VALID_TRANSACTION_TYPES:
            return {
                'valid': False,
                'error': f'Invalid transaction type. Must be one of: {DataValidator.VALID_TRANSACTION_TYPES}',
                'sanitized_type': 'debit'
            }
        
        return {
            'valid': True,
            'error': None,
            'sanitized_type': normalized_type
        }
    
    @staticmethod
    def validate_category(category: Optional[str]) -> Dict[str, Any]:
        """Validate and sanitize category"""
        if not category:
            return {
                'valid': True,
                'error': None,
                'sanitized_category': 'other'
            }
        
        normalized_category = category.lower().strip()
        
        if normalized_category not in DataValidator.VALID_CATEGORIES:
            logger.info(f"Unknown category '{category}', defaulting to 'other'")
            return {
                'valid': True,
                'error': None,
                'sanitized_category': 'other'
            }
        
        return {
            'valid': True,
            'error': None,
            'sanitized_category': normalized_category
        }
    
    @staticmethod
    def detect_outliers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect outliers in transaction data using statistical methods"""
        if len(transactions) < 3:
            return transactions
        
        amounts = [t.get('amount', 0) for t in transactions if t.get('amount')]
        
        if not amounts:
            return transactions
        
        # Calculate IQR for outlier detection
        amounts.sort()
        n = len(amounts)
        q1 = amounts[n // 4]
        q3 = amounts[3 * n // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Mark outliers
        for transaction in transactions:
            amount = transaction.get('amount', 0)
            if amount < lower_bound or amount > upper_bound:
                transaction['is_outlier'] = True
                transaction['outlier_reason'] = 'Statistical outlier (IQR method)'
            else:
                transaction['is_outlier'] = False
        
        return transactions
    
    @staticmethod
    def validate_transaction_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation of transaction data"""
        errors = []
        validated_data = {}
        
        # Validate each field
        validations = [
            ('amount', DataValidator.validate_amount(data.get('amount'))),
            ('date', DataValidator.validate_date(data.get('date'))),
            ('vendor', DataValidator.validate_vendor(data.get('vendor'))),
            ('transaction_type', DataValidator.validate_transaction_type(data.get('transaction_type'))),
            ('category', DataValidator.validate_category(data.get('category')))
        ]
        
        for field, validation in validations:
            if validation['valid']:
                validated_data[field] = validation[f'sanitized_{field}']
                if validation.get('is_outlier'):
                    validated_data['is_outlier'] = True
                    validated_data['outlier_reason'] = validation['outlier_reason']
            else:
                errors.append(f"{field}: {validation['error']}")
                # Use sanitized value even if invalid for partial recovery
                if validation.get(f'sanitized_{field}') is not None:
                    validated_data[field] = validation[f'sanitized_{field}']
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'data': validated_data
        }
