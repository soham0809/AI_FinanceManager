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
        """Extract amount from SMS"""
        amount_patterns = [
            r'Rs\.(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'₹(\d+(?:,\d+)*(?:\.\d{2})?)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, sms_text)
            if match:
                amount_str = match.group(1).replace(',', '')
                return float(amount_str)
        return None

    def extract_vendor(self, sms_text: str) -> str:
        """Extract vendor from SMS"""
        vendor_patterns = [
            r'at\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\.|$)',
            r'to\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\.|$)',
            r'from\s+([A-Z][A-Z0-9\s&.-]+?)(?:\s+on|\.|$)'
        ]
        
        for pattern in vendor_patterns:
            match = re.search(pattern, sms_text)
            if match:
                return match.group(1).strip()
        return "Unknown"

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

    def parse_transaction(self, sms_text: str) -> Dict[str, Any]:
        """Parse SMS and extract transaction details"""
        bank = self.identify_bank(sms_text)
        amount = self.extract_amount(sms_text)
        
        if not amount:
            return {
                'success': False,
                'error': 'Could not extract amount',
                'confidence': 0.0
            }
        
        vendor = self.extract_vendor(sms_text)
        date_str = self.extract_date(sms_text)
        
        # Determine transaction type
        transaction_type = 'credit' if 'credited' in sms_text.lower() else 'debit'
        
        # Determine category based on vendor
        category = self.categorize_transaction(vendor, sms_text)
        
        return {
            'success': True,
            'vendor': vendor,
            'amount': amount,
            'date': date_str,
            'transaction_type': transaction_type,
            'category': category,
            'raw_text': sms_text,
            'confidence': 0.8,
            'bank': bank
        }

    def categorize_transaction(self, vendor: str, sms_text: str) -> str:
        """Categorize transaction based on vendor and SMS content"""
        vendor_lower = vendor.lower()
        sms_lower = sms_text.lower()
        
        # Food & Dining
        if any(keyword in vendor_lower for keyword in ['swiggy', 'zomato', 'dominos', 'mcdonald', 'kfc', 'pizza', 'restaurant']):
            return 'Food & Dining'
        
        # Shopping
        if any(keyword in vendor_lower for keyword in ['amazon', 'flipkart', 'myntra', 'ajio', 'shopping', 'mall']):
            return 'Shopping'
        
        # Transportation
        if any(keyword in vendor_lower for keyword in ['uber', 'ola', 'rapido', 'metro', 'bus', 'taxi']):
            return 'Transportation'
        
        # Utilities
        if any(keyword in vendor_lower for keyword in ['jio', 'airtel', 'vodafone', 'bsnl', 'electricity', 'gas']):
            return 'Utilities'
        
        # Entertainment
        if any(keyword in vendor_lower for keyword in ['netflix', 'amazon prime', 'hotstar', 'spotify', 'movie', 'cinema']):
            return 'Entertainment'
        
        # Financial
        if any(keyword in sms_lower for keyword in ['upi', 'transfer', 'payment', 'bank']):
            return 'Financial'
        
        return 'Others'
