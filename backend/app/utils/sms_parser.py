"""SMS parsing utilities"""
import re
from datetime import datetime
from typing import Dict, Any, Optional

class SMSParser:
    def __init__(self):
        self.bank_patterns = {
            'hdfc': {
                'name': 'HDFC Bank',
                'debit_pattern': r'HDFC Bank.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*debited.*at\s+([A-Z][A-Z0-9\s&.-]+)',
                'credit_pattern': r'HDFC Bank.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*credited',
                'date_pattern': r'on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
            },
            'sbi': {
                'name': 'SBI',
                'debit_pattern': r'SBI.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*debited.*at\s+([A-Z][A-Z0-9\s&.-]+)',
                'credit_pattern': r'SBI.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*credited',
                'date_pattern': r'on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
            },
            'icici': {
                'name': 'ICICI Bank',
                'debit_pattern': r'ICICI Bank.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*debited.*at\s+([A-Z][A-Z0-9\s&.-]+)',
                'credit_pattern': r'ICICI Bank.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*credited',
                'date_pattern': r'on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
            },
            'canara': {
                'name': 'Canara Bank',
                'debit_pattern': r'Canara Bank.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*debited.*at\s+([A-Z][A-Z0-9\s&.-]+)',
                'credit_pattern': r'Canara Bank.*Rs\.(\d+(?:,\d+)*(?:\.\d{2})?).*credited',
                'date_pattern': r'on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
            }
        }

    def identify_bank(self, sms_text: str) -> Optional[str]:
        """Identify bank from SMS text"""
        sms_lower = sms_text.lower()
        for bank_key, bank_info in self.bank_patterns.items():
            if bank_info['name'].lower() in sms_lower:
                return bank_key
        return None

    def extract_amount(self, sms_text: str) -> Optional[float]:
        """Extract amount from SMS with more robust patterns"""
        # More specific patterns that require transaction context
        amount_patterns = [
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:debited|credited|spent|paid|transferred)',
            r'(?:debited|credited|spent|paid|transferred).*?Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:debited|credited|spent|paid|transferred)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:debited|credited|spent|paid|transferred)',
            # Fallback patterns
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    # Validate amount is reasonable (between 1 and 1,000,000)
                    if 1 <= amount <= 1000000:
                        return amount
                except ValueError:
                    continue
        return None

    def extract_vendor(self, sms_text: str) -> str:
        """Extract vendor from SMS with enhanced patterns"""
        # More comprehensive vendor extraction patterns
        vendor_patterns = [
            # UPI patterns
            r'(?:paid to|transferred to)\s+([A-Z][A-Z0-9\s@._-]+?)(?:\s+via\s+UPI|\s+using|\s+on|\.|$)',
            r'UPI.*?to\s+([A-Z][A-Z0-9\s@._-]+?)(?:\s+on|\s+using|\.|$)',
            r'VPA\s+([A-Z][A-Z0-9\s@._-]+?)(?:\s+UPI|\s+on|\.|$)',
            
            # Card/Bank patterns  
            r'(?:debited|spent)\s+(?:from|at)\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s+using|\.|$)',
            r'at\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s+using|\s+via|\.|$)',
            r'to\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s+via|\.|$)',
            r'from\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\s+via|\.|$)',
            
            # Merchant patterns
            r'merchant\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\.|$)',
            r'payment\s+to\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\.|$)'
        ]
        
        for pattern in vendor_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                # Clean up vendor name
                vendor = re.sub(r'\s+', ' ', vendor)  # Multiple spaces to single
                vendor = re.sub(r'[^\w\s@.-]', '', vendor)  # Remove special chars except allowed
                if len(vendor) >= 3:  # Minimum vendor name length
                    return vendor[:50]  # Limit length
        
        # Fallback: look for known merchant patterns
        known_merchants = [
            'SWIGGY', 'ZOMATO', 'AMAZON', 'FLIPKART', 'PAYTM', 'GPAY', 'PHONEPE',
            'UBER', 'OLA', 'JIO', 'AIRTEL', 'NETFLIX', 'SPOTIFY', 'MYNTRA'
        ]
        
        for merchant in known_merchants:
            if merchant in sms_text.upper():
                return merchant.title()
        
        return "Unknown Merchant"

    def extract_date(self, sms_text: str) -> str:
        """Extract and format date from SMS"""
        date_patterns = [
            r'on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, sms_text)
            if match:
                date_str = match.group(1)
                return self.format_date(date_str)
        
        return datetime.now().strftime('%Y-%m-%d')

    def format_date(self, date_str: str) -> str:
        """Format date string to YYYY-MM-DD"""
        try:
            # Handle different separators and year formats
            if len(date_str.split('-')[-1]) == 2 or len(date_str.split('/')[-1]) == 2:
                # 2-digit year
                if '-' in date_str:
                    parsed_date = datetime.strptime(date_str, '%d-%m-%y')
                else:
                    parsed_date = datetime.strptime(date_str, '%d/%m/%y')
                # Ensure 2-digit years are in 2000s
                if parsed_date.year < 2000:
                    parsed_date = parsed_date.replace(year=parsed_date.year + 100)
            else:
                # 4-digit year
                if '-' in date_str:
                    parsed_date = datetime.strptime(date_str, '%d-%m-%Y')
                else:
                    parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
            
            # Validate date is reasonable
            current_date = datetime.now()
            if parsed_date > current_date:
                return current_date.strftime('%Y-%m-%d')
            elif parsed_date < datetime(2020, 1, 1):
                return current_date.strftime('%Y-%m-%d')
            else:
                return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            return datetime.now().strftime('%Y-%m-%d')

    def is_valid_transaction_sms(self, sms_text: str) -> bool:
        """Check if SMS contains valid transaction keywords"""
        transaction_keywords = [
            'debited', 'credited', 'spent', 'paid', 'transferred', 'payment',
            'upi', 'transaction', 'purchase', 'withdrawal', 'deposit',
            'recharge', 'successful', 'completed'
        ]
        
        sms_lower = sms_text.lower()
        return any(keyword in sms_lower for keyword in transaction_keywords)

    def parse_transaction(self, sms_text: str) -> Dict[str, Any]:
        """Parse SMS and extract transaction details with enhanced validation"""
        # First check if this looks like a transaction SMS
        if not self.is_valid_transaction_sms(sms_text):
            return {
                'success': False,
                'error': 'SMS does not contain transaction keywords',
                'confidence': 0.0
            }
        
        bank = self.identify_bank(sms_text)
        amount = self.extract_amount(sms_text)
        
        if not amount:
            return {
                'success': False,
                'error': 'Could not extract valid amount from transaction SMS',
                'confidence': 0.0
            }
        
        vendor = self.extract_vendor(sms_text)
        date_str = self.extract_date(sms_text)
        
        # Determine transaction type with more specific patterns
        transaction_type = 'debit'  # Default to debit
        if any(word in sms_text.lower() for word in ['credited', 'received', 'refund', 'cashback']):
            transaction_type = 'credit'
        
        # Determine category based on vendor and SMS content
        category = self.categorize_transaction(vendor, sms_text)
        
        # Calculate confidence based on extraction quality
        confidence = 0.6  # Base confidence
        if bank:
            confidence += 0.1
        if vendor != "Unknown Merchant":
            confidence += 0.1
        if len(vendor) > 5:
            confidence += 0.1
        if amount > 0:
            confidence += 0.1
        
        return {
            'success': True,
            'vendor': vendor,
            'amount': amount,
            'date': date_str,
            'transaction_type': transaction_type,
            'category': category,
            'raw_text': sms_text,
            'confidence': min(confidence, 1.0),
            'bank': bank,
            'parsing_info': f"₹{amount} for {vendor}"
        }

    def categorize_transaction(self, vendor: str, sms_text: str) -> str:
        """Enhanced categorization based on vendor and SMS content with specific keywords"""
        vendor_lower = vendor.lower()
        sms_lower = sms_text.lower()
        
        # Food & Dining - More comprehensive
        food_keywords = ['swiggy', 'zomato', 'dominos', 'mcdonald', 'kfc', 'pizza', 'restaurant', 
                        'cafe', 'food', 'dining', 'burger', 'biryani', 'kitchen', 'eatery']
        if any(keyword in vendor_lower for keyword in food_keywords):
            return 'Food & Dining'
        
        # Shopping - Enhanced
        shopping_keywords = ['amazon', 'flipkart', 'myntra', 'ajio', 'shopping', 'mall', 'store',
                           'retail', 'market', 'bazaar', 'shop', 'purchase', 'buy']
        if any(keyword in vendor_lower for keyword in shopping_keywords):
            return 'Shopping'
        
        # Transportation - More specific
        transport_keywords = ['uber', 'ola', 'rapido', 'metro', 'bus', 'taxi', 'cab', 'auto',
                            'transport', 'travel', 'ride', 'booking', 'ticket']
        if any(keyword in vendor_lower for keyword in transport_keywords):
            return 'Transportation'
        
        # Utilities - Expanded
        utility_keywords = ['jio', 'airtel', 'vodafone', 'bsnl', 'electricity', 'gas', 'water',
                          'internet', 'broadband', 'mobile', 'recharge', 'bill', 'utility']
        if any(keyword in vendor_lower for keyword in utility_keywords):
            return 'Utilities'
        
        # Entertainment - More options
        entertainment_keywords = ['netflix', 'prime', 'hotstar', 'spotify', 'movie', 'cinema',
                                'entertainment', 'music', 'streaming', 'subscription', 'game']
        if any(keyword in vendor_lower for keyword in entertainment_keywords):
            return 'Entertainment'
        
        # Healthcare - New category
        health_keywords = ['hospital', 'clinic', 'medical', 'pharmacy', 'doctor', 'health',
                         'medicine', 'treatment', 'consultation']
        if any(keyword in vendor_lower for keyword in health_keywords):
            return 'Healthcare'
        
        # Education - New category  
        education_keywords = ['school', 'college', 'university', 'education', 'course', 'training',
                            'learning', 'academy', 'institute', 'tuition']
        if any(keyword in vendor_lower for keyword in education_keywords):
            return 'Education'
        
        # Financial Services
        financial_keywords = ['bank', 'atm', 'transfer', 'payment', 'wallet', 'paytm', 'gpay', 
                            'phonepe', 'upi', 'loan', 'emi', 'insurance']
        if any(keyword in vendor_lower for keyword in financial_keywords) or \
           any(keyword in sms_lower for keyword in ['upi', 'transfer', 'payment']):
            return 'Financial'
        
        return 'Others'
