import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from data_validator import DataValidator
from dataclasses import dataclass

@dataclass
class ParsedTransaction:
    vendor: str
    amount: float
    date: str
    transaction_type: str
    category: Optional[str] = None
    success: bool = True
    raw_text: str = ""
    confidence: float = 0.0

class EnhancedSMSParser:
    def __init__(self):
        self.bank_patterns = self._load_bank_patterns()
        self.vendor_categories = self._load_vendor_categories()
        
    def _load_bank_patterns(self) -> Dict:
        """Load comprehensive patterns for Indian banks and UPI providers"""
        return {
            # State Bank of India (SBI)
            'sbi': {
                'debit': [
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?from.*?a/c.*?\*+(\d+).*?(?:at|to)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s+for|\s*\.)',
                    r'amount\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?(?:at|to)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                ],
                'credit': [
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*credited.*?to.*?a/c.*?\*+(\d+).*?(?:from|by)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                    r'amount\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*credited.*?(?:from|by)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                ]
            },
            
            # HDFC Bank
            'hdfc': {
                'debit': [
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?hdfc.*?(?:at|to)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                    r'spent\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:at|on)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+using|\s*\.)',
                ],
                'credit': [
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*credited.*?hdfc.*?(?:from|by)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                ]
            },
            
            # ICICI Bank
            'icici': {
                'debit': [
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?icici.*?(?:at|to)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                    r'transaction\s*of\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:at|on)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+using|\s*\.)',
                ],
                'credit': [
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*credited.*?icici.*?(?:from|by)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                ]
            },
            
            # UPI Providers (GPay, PhonePe, Paytm, etc.)
            'upi': {
                'debit': [
                    r'(?:paid|sent)\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*to\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+via\s+upi|\s+using)',
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:paid|sent)\s*(?:to|at)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+via|\s+using|\s*\.)',
                    r'amount\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:paid|debited).*?(?:to|at)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+via|\s*\.)',
                ],
                'credit': [
                    r'(?:received|got)\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*from\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+via\s+upi|\s+using)',
                    r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:received|credited)\s*from\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+via|\s*\.)',
                ]
            },
            
            # Generic patterns for other banks
            'generic': {
                'debit': [
                    r'(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:debited|spent|paid).*?(?:at|to|on)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s+for|\s*\.|\s*,|$)',
                    r'(?:debited|spent|paid)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:at|to|on)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.|\s*,|$)',
                    r'transaction\s*(?:of\s*)?(?:rs\.?|inr|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:at|on)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.)',
                ],
                'credit': [
                    r'(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:credited|received).*?(?:from|by)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.|\s*,|$)',
                    r'(?:credited|received)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:from|by)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s*\.|\s*,|$)',
                ]
            }
        }
    
    def _load_vendor_categories(self) -> Dict[str, str]:
        """Load vendor to category mappings"""
        return {
            # Food & Dining
            'swiggy': 'Food & Dining',
            'zomato': 'Food & Dining',
            'dominos': 'Food & Dining',
            'pizza hut': 'Food & Dining',
            'mcdonalds': 'Food & Dining',
            'kfc': 'Food & Dining',
            'subway': 'Food & Dining',
            'cafe coffee day': 'Food & Dining',
            'starbucks': 'Food & Dining',
            
            # Shopping
            'amazon': 'Shopping',
            'flipkart': 'Shopping',
            'myntra': 'Shopping',
            'ajio': 'Shopping',
            'nykaa': 'Shopping',
            'big basket': 'Shopping',
            'grofers': 'Shopping',
            'blinkit': 'Shopping',
            'dunzo': 'Shopping',
            
            # Transportation
            'uber': 'Transportation',
            'ola': 'Transportation',
            'rapido': 'Transportation',
            'metro': 'Transportation',
            'irctc': 'Transportation',
            'redbus': 'Transportation',
            'makemytrip': 'Transportation',
            'goibibo': 'Transportation',
            
            # Entertainment
            'netflix': 'Entertainment',
            'amazon prime': 'Entertainment',
            'hotstar': 'Entertainment',
            'spotify': 'Entertainment',
            'youtube': 'Entertainment',
            'bookmyshow': 'Entertainment',
            'paytm movies': 'Entertainment',
            
            # Utilities
            'electricity': 'Utilities',
            'gas': 'Utilities',
            'water': 'Utilities',
            'internet': 'Utilities',
            'mobile': 'Utilities',
            'airtel': 'Utilities',
            'jio': 'Utilities',
            'vi': 'Utilities',
            'bsnl': 'Utilities',
            
            # Healthcare
            'apollo': 'Healthcare',
            'fortis': 'Healthcare',
            'max': 'Healthcare',
            'practo': 'Healthcare',
            'pharmeasy': 'Healthcare',
            '1mg': 'Healthcare',
            'netmeds': 'Healthcare',
            
            # Education
            'byju': 'Education',
            'unacademy': 'Education',
            'vedantu': 'Education',
            'coursera': 'Education',
            'udemy': 'Education',
            
            # Financial
            'sbi': 'Financial',
            'hdfc': 'Financial',
            'icici': 'Financial',
            'axis': 'Financial',
            'kotak': 'Financial',
            'paytm': 'Financial',
            'phonepe': 'Financial',
            'gpay': 'Financial',
            'googlepay': 'Financial',
        }
    
    def parse_sms(self, sms_text: str) -> Dict[str, Any]:
        """
        Enhanced SMS parsing with robust error handling and validation
        """
        try:
            # Validate SMS text input
            sms_validation = DataValidator.validate_sms_text(sms_text)
            if not sms_validation['valid']:
                return {
                    'success': False,
                    'error': sms_validation['error'],
                    'error_type': 'VALIDATION_ERROR',
                    'raw_text': sms_text
                }
            
            sanitized_sms = sms_validation['sanitized_text']
            sms_lower = sanitized_sms.lower()
            
            # Try to extract transaction details using multiple patterns
            extracted_data = self._extract_transaction_details(sanitized_sms)
            
            if not extracted_data:
                return {
                    'success': False,
                    'error': 'No transaction pattern matched in SMS',
                    'error_type': 'PATTERN_MISMATCH',
                    'raw_text': sms_text,
                    'suggestions': [
                        'Ensure SMS contains amount, vendor, and transaction type',
                        'Check if SMS is from a recognized bank or UPI service'
                    ]
                }
            
            # Validate and sanitize extracted data
            validation_result = DataValidator.validate_transaction_data({
                'amount': extracted_data.get('amount'),
                'vendor': extracted_data.get('vendor', 'Unknown'),
                'transaction_type': extracted_data.get('transaction_type', 'debit'),
                'date': extracted_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'category': self._categorize_transaction(
                    extracted_data.get('vendor', ''), sanitized_sms
                )
            })
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Data validation failed: {'; '.join(validation_result['errors'])}",
                    'error_type': 'VALIDATION_ERROR',
                    'raw_text': sms_text,
                    'validation_errors': validation_result['errors']
                }
            
            validated_data = validation_result['data']
            
            # Calculate confidence score
            confidence = self._calculate_confidence(extracted_data, sanitized_sms)
            
            # Check for outliers
            if validated_data.get('is_outlier'):
                confidence *= 0.7  # Reduce confidence for outliers
            
            return {
                'success': True,
                'vendor': validated_data['vendor'],
                'amount': validated_data['amount'],
                'date': validated_data['date'],
                'transaction_type': validated_data['transaction_type'],
                'category': validated_data['category'],
                'confidence': confidence,
                'raw_text': sms_text,
                'extraction_method': extracted_data.get('method', 'pattern_matching'),
                'is_outlier': validated_data.get('is_outlier', False),
                'outlier_reason': validated_data.get('outlier_reason')
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': f"Data validation error: {str(e)}",
                'error_type': 'VALIDATION_ERROR',
                'raw_text': sms_text
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error during SMS parsing: {str(e)}",
                'error_type': 'PARSING_ERROR',
                'raw_text': sms_text
            }
    
    def _identify_bank_type(self, sms_lower: str) -> str:
        """Identify the bank or UPI provider from SMS"""
        if any(bank in sms_lower for bank in ['sbi', 'state bank']):
            return 'sbi'
        elif 'hdfc' in sms_lower:
            return 'hdfc'
        elif 'icici' in sms_lower:
            return 'icici'
        elif any(upi in sms_lower for upi in ['upi', 'gpay', 'phonepe', 'paytm', 'googlepay']):
            return 'upi'
        else:
            return 'generic'
    
    def _extract_transaction_data(self, sms_text: str, sms_lower: str, bank_type: str) -> Tuple[Optional[float], str, str, float]:
        """Extract amount, vendor, transaction type with confidence score"""
        # Special case for HDFC Bank format that we're having trouble with
        hdfc_pattern = r'hdfc bank:?\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?a/c.*?on\s+\d{1,2}-\d{1,2}-\d{4}\s+at\s+([A-Za-z][A-Za-z0-9\s&.-]+)'
        match = re.search(hdfc_pattern, sms_lower)
        if match:
            amount_str = match.group(1).replace(',', '')
            amount = float(amount_str)
            vendor = self._clean_vendor_name(match.group(2).strip())
            return amount, vendor, "debit", 0.95
            
        patterns = self.bank_patterns.get(bank_type, self.bank_patterns['generic'])
        
        # Try debit patterns first
        for pattern in patterns.get('debit', []):
            match = re.search(pattern, sms_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                vendor = self._clean_vendor_name(match.group(2).strip()) if len(match.groups()) > 1 else "Unknown"
                return amount, vendor, "debit", 0.9
        
        # Try credit patterns
        for pattern in patterns.get('credit', []):
            match = re.search(pattern, sms_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                vendor = self._clean_vendor_name(match.group(2).strip()) if len(match.groups()) > 1 else "Unknown"
                return amount, vendor, "credit", 0.9
        
        # Enhanced fallback patterns
        enhanced_patterns = [
            # Pattern for "paid to VENDOR" or "sent to VENDOR"
            (r'(?:paid|sent)\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*to\s+([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+via|\s+using|\s+on|\s*\.)', 'debit'),
            # Pattern for "received from VENDOR"
            (r'(?:received|got)\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*from\s+([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+via|\s+on|\s*\.)', 'credit'),
            # Pattern for "at VENDOR" or "on VENDOR"
            (r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:debited|spent|paid).*?(?:at|on)\s+([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+on|\s+for|\s+via|\s*\.)', 'debit'),
            # Pattern for "made to VENDOR"
            (r'(?:payment|amount)\s*(?:of\s*)?rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:made\s*)?to\s+([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+via|\s+on|\s*\.)', 'debit'),
            # Pattern for "debited for VENDOR"
            (r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited\s*(?:for|from)?\s*([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+via|\s+on|\s*\.)', 'debit'),
            # HDFC Bank specific pattern
            (r'hdfc\s*bank.*?rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?(?:at|to)\s+([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+on|\s+for|\s+via|\s*\.)', 'debit'),
            # HDFC Bank format with account number
            (r'hdfc\s*bank.*?rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?a/c.*?(?:at|to)\s+([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+on|\s+for|\s+via|\s*\.)', 'debit'),
            # HDFC Bank format with account number and date
            (r'hdfc\s*bank.*?rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?a/c.*?on\s+\d{2}-\d{2}-\d{4}\s+at\s+([A-Za-z][A-Za-z0-9\s&.-]+?)(?:\s+on|\s+for|\s+via|\s*\.)', 'debit'),
            # HDFC Bank format with account number and date (simplified)
            (r'hdfc\s*bank.*?rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?a/c.*?on\s+\d{1,2}-\d{1,2}-\d{4}\s+at\s+([A-Za-z][A-Za-z0-9\s&.-]+)', 'debit'),
            # HDFC Bank format with account number (most simplified)
            (r'hdfc\s*bank:?\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*debited.*?a/c.*?\s+at\s+([A-Za-z][A-Za-z0-9\s&.-]+)', 'debit'),
        ]
        
        for pattern, trans_type in enhanced_patterns:
            match = re.search(pattern, sms_lower)
            if match:
                amount = float(match.group(1).replace(',', ''))
                vendor = self._clean_vendor_name(match.group(2).strip())
                return amount, vendor, trans_type, 0.8
        
        # Final fallback to basic amount extraction
        amount_match = re.search(r'(?:rs\.?|inr|₹)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', sms_lower)
        if amount_match:
            amount = float(amount_match.group(1).replace(',', ''))
            
            # Determine transaction type from keywords
            transaction_type = "debit"
            if any(word in sms_lower for word in ['credited', 'received', 'refund', 'cashback']):
                transaction_type = "credit"
            
            # Try to extract vendor name
            vendor = self._extract_vendor_fallback(sms_text)
            
            return amount, vendor, transaction_type, 0.6
        
        return None, "Unknown", "unknown", 0.0
    
    def _clean_vendor_name(self, vendor: str) -> str:
        """Clean vendor name by removing common suffixes and prefixes"""
        # Remove common suffixes
        suffixes_to_remove = [
            r'\s+via\s+.*$',
            r'\s+using\s+.*$',
            r'\s+on\s+\d{2}-\w{3}-\d{2}.*$',
            r'\s+for\s+.*$',
            r'\s+upi.*$',
            r'\s+transaction.*$',
        ]
        
        cleaned = vendor
        for suffix in suffixes_to_remove:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _extract_vendor_fallback(self, sms_text: str) -> str:
        """Fallback vendor extraction"""
        # Look for common vendor patterns
        vendor_patterns = [
            r'(?:at|to|from|merchant)\s+([A-Z][A-Z0-9\s&.-]{2,30}?)(?:\s+on|\s+for|\s*\.|\s*,|$)',
            r'([A-Z][A-Z0-9\s&.-]{3,20})\s+(?:transaction|payment|purchase)',
        ]
        
        for pattern in vendor_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown Merchant"
    
    def _extract_transaction_details(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """Extract transaction details from SMS text"""
        sms_lower = sms_text.lower()
        bank_type = self._identify_bank_type(sms_lower)
        
        # Extract amount, vendor, transaction type
        amount, vendor, transaction_type, confidence = self._extract_transaction_data(
            sms_text, sms_lower, bank_type
        )
        
        if amount is None:
            return None
        
        # Extract date (use current date if not found)
        date_str = self._extract_date(sms_text)
        
        return {
            'amount': amount,
            'vendor': vendor,
            'transaction_type': transaction_type,
            'date': date_str,
            'method': f'{bank_type}_pattern',
            'confidence': confidence
        }
    
    def _extract_date(self, sms_text: str) -> str:
        """Extract date from SMS text or use current date"""
        import re
        from datetime import datetime
        
        # Common date patterns in SMS
        date_patterns = [
            r'(\d{2}-\w{3}-\d{2})',  # 12-Jan-23
            r'(\d{2}/\d{2}/\d{4})',  # 12/01/2023
            r'(\d{2}-\d{2}-\d{4})',  # 12-01-2023
            r'on (\d{2}-\w{3}-\d{4})',  # on 12-Jan-2023
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, sms_text)
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse and standardize the date
                    if '-' in date_str and len(date_str.split('-')[1]) == 3:  # 12-Jan-23 format
                        parsed_date = datetime.strptime(date_str, '%d-%b-%y')
                    elif '/' in date_str:
                        parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
                    elif '-' in date_str:
                        parsed_date = datetime.strptime(date_str, '%d-%m-%Y')
                    else:
                        continue
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        # Default to current date if no date found
        return datetime.now().strftime('%Y-%m-%d')
    
    def _categorize_transaction(self, vendor: str, sms_text: str) -> Optional[str]:
        """Categorize transaction based on vendor and SMS content"""
        # First try ML categorization if available
        ml_category = self._categorize_vendor(vendor)
        if ml_category:
            return ml_category
        
        # Fallback to keyword-based categorization from SMS content
        sms_lower = sms_text.lower()
        
        # Enhanced keyword matching from SMS content
        if any(word in sms_lower for word in ['swiggy', 'zomato', 'food', 'restaurant', 'cafe', 'pizza', 'burger']):
            return 'Food & Dining'
        elif any(word in sms_lower for word in ['amazon', 'flipkart', 'shopping', 'store', 'mall']):
            return 'Shopping'
        elif any(word in sms_lower for word in ['uber', 'ola', 'fuel', 'petrol', 'transport']):
            return 'Transportation'
        elif any(word in sms_lower for word in ['netflix', 'movie', 'entertainment', 'game']):
            return 'Entertainment'
        elif any(word in sms_lower for word in ['hospital', 'medical', 'pharmacy', 'doctor']):
            return 'Healthcare'
        elif any(word in sms_lower for word in ['electricity', 'bill', 'recharge', 'mobile', 'internet']):
            return 'Utilities'
        else:
            return 'Others'
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any], sms_text: str) -> float:
        """Calculate confidence score for the extraction"""
        confidence = extracted_data.get('confidence', 0.0)
        
        # Boost confidence based on various factors
        if extracted_data.get('amount') and extracted_data.get('vendor'):
            confidence += 0.2
        
        if extracted_data.get('transaction_type') in ['debit', 'credit']:
            confidence += 0.1
        
        # Check if SMS contains bank/UPI keywords
        sms_lower = sms_text.lower()
        if any(word in sms_lower for word in ['bank', 'upi', 'debited', 'credited', 'paid', 'received']):
            confidence += 0.1
        
        # Penalize if vendor is "Unknown"
        if extracted_data.get('vendor') == 'Unknown':
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _categorize_vendor(self, vendor: str) -> Optional[str]:
        """Categorize vendor using ML model with fallback to rule-based"""
        # Try ML categorization first
        try:
            from ml_categorizer import ml_categorizer
            ml_category, confidence = ml_categorizer.predict_category(vendor)
            
            # Use ML prediction if confidence is high enough
            if confidence > 0.3:  # Threshold for ML confidence
                return ml_category
        except ImportError:
            pass  # Fall back to rule-based if ML not available
        
        # Fallback to rule-based categorization
        vendor_lower = vendor.lower()
        
        # Direct vendor mapping (highest priority)
        for vendor_key, category in self.vendor_categories.items():
            if vendor_key in vendor_lower:
                return category
        
        # Keyword-based categorization with better patterns
        food_keywords = ['restaurant', 'cafe', 'food', 'kitchen', 'pizza', 'burger', 'swiggy', 'zomato', 'dominos', 'kfc', 'mcdonalds']
        shopping_keywords = ['store', 'mart', 'shop', 'retail', 'mall', 'amazon', 'flipkart', 'myntra', 'dunzo', 'blinkit']
        fuel_keywords = ['fuel', 'petrol', 'diesel', 'gas', 'hp', 'ioc', 'bpcl', 'pump']
        healthcare_keywords = ['medical', 'hospital', 'clinic', 'pharmacy', 'doctor', 'apollo', 'pharmeasy', '1mg']
        education_keywords = ['school', 'college', 'university', 'education', 'course', 'byju', 'unacademy', 'classes']
        transport_keywords = ['uber', 'ola', 'rapido', 'taxi', 'cab', 'metro', 'bus', 'train', 'irctc']
        entertainment_keywords = ['netflix', 'prime', 'hotstar', 'spotify', 'youtube', 'movie', 'cinema', 'bookmyshow']
        utilities_keywords = ['electricity', 'electric', 'bill', 'water', 'gas', 'internet', 'mobile', 'recharge', 'airtel', 'jio']
        
        if any(word in vendor_lower for word in food_keywords):
            return 'Food & Dining'
        elif any(word in vendor_lower for word in shopping_keywords):
            return 'Shopping'
        elif any(word in vendor_lower for word in fuel_keywords):
            return 'Fuel'
        elif any(word in vendor_lower for word in healthcare_keywords):
            return 'Healthcare'
        elif any(word in vendor_lower for word in education_keywords):
            return 'Education'
        elif any(word in vendor_lower for word in transport_keywords):
            return 'Transportation'
        elif any(word in vendor_lower for word in entertainment_keywords):
            return 'Entertainment'
        elif any(word in vendor_lower for word in utilities_keywords):
            return 'Utilities'
        
        return None

# Global parser instance
sms_parser = EnhancedSMSParser()
