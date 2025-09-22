"""Gemini AI integration for intelligent SMS parsing"""
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.config.settings import settings

class GeminiAssistant:
    def __init__(self):
        self.initialized = False
        self.model = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """Initialize Gemini AI"""
        try:
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                self.initialized = True
                print("Gemini AI initialized successfully")
            else:
                print("Gemini API key not found")
        except Exception as e:
            print(f"Failed to initialize Gemini AI: {e}")
            self.initialized = False
    
    def parse_sms_transaction(self, sms_text: str) -> Dict[str, Any]:
        """Parse SMS using Gemini AI for intelligent extraction"""
        if not self.initialized:
            return {
                'success': False,
                'error': 'Gemini AI not initialized',
                'is_promotional': False
            }
        
        try:
            prompt = f"""
            Analyze this SMS and determine if it's a real financial transaction. If it is, extract the details.
            
            SMS: "{sms_text}"
            
            If it's a REAL transaction (money debited/credited), return:
            {{
                "is_transaction": true,
                "vendor": "<merchant/vendor name>",
                "amount": <numeric amount>,
                "transaction_type": "<debit or credit>",
                "category": "<one of: Food & Dining, Shopping, Transportation, Entertainment, Healthcare, Education, Utilities, Fuel, Financial, Others>",
                "confidence": <confidence score 0.0 to 1.0>,
                "date": "<transaction date in DD-MM-YYYY format from SMS or null if not found>",
                "account_info": "<last 4 digits of account/card or null if not found>",
                "transaction_id": "<UPI ref/transaction ID if available or null>"
            }}
            
            If it's NOT a transaction (promotional, OTP, balance inquiry, etc.), return:
            {{
                "is_transaction": false,
                "reason": "<brief reason why it's not a transaction>",
                "confidence": 0.0
            }}
            
            Rules:
            - Be strict about what constitutes a real transaction
            - Promotional messages, OTPs, offers, alerts are NOT transactions
            - Only actual money movement (debit/credit) counts as transaction
            - Extract transaction_id/UPI ref for duplicate detection
            - Extract the EXACT date from SMS text
            - If no date found in SMS, set date to null
            - Set high confidence only for clear, unambiguous transactions
            - Return ONLY the JSON object, no additional text
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                # Clean the response text to extract JSON
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3].strip()
                
                parsed_data = json.loads(response_text)
                
                # Check if it's a real transaction
                if not parsed_data.get('is_transaction', False):
                    return {
                        'success': False,
                        'error': parsed_data.get('reason', 'Not a transaction'),
                        'is_promotional': True
                    }
                
                # Return successful transaction data
                return {
                    'success': True,
                    'transaction_data': parsed_data,
                    'is_promotional': False
                }
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Response text: {response_text}")
                return {
                    'success': False,
                    'error': f'Failed to parse Gemini response: {e}',
                    'is_promotional': False
                }
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                'success': False,
                'error': f'Gemini API error: {e}',
                'is_promotional': False
            }
    
    def analyze_spending_patterns(self, transactions: list) -> Dict[str, Any]:
        """Analyze spending patterns using Gemini AI"""
        if not self.initialized or not transactions:
            return {'success': False, 'error': 'No data or Gemini not initialized'}
        
        try:
            # Prepare transaction summary for analysis
            transaction_summary = []
            for t in transactions[:20]:  # Limit to recent 20 transactions
                transaction_summary.append({
                    'vendor': t.vendor,
                    'amount': t.amount,
                    'category': t.category,
                    'date': t.date.strftime('%Y-%m-%d'),
                    'type': t.transaction_type
                })
            
            prompt = f"""
            Analyze these financial transactions and provide insights:
            
            Transactions: {json.dumps(transaction_summary, indent=2)}
            
            Provide analysis in this JSON format:
            {{
                "spending_insights": ["insight1", "insight2", "insight3"],
                "recommendations": ["recommendation1", "recommendation2"],
                "risk_factors": ["risk1", "risk2"],
                "positive_patterns": ["pattern1", "pattern2"]
            }}
            
            Focus on:
            - Spending habits and patterns
            - Budget recommendations
            - Potential savings opportunities
            - Financial health indicators
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            analysis = json.loads(response_text)
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            print(f"Spending analysis error: {e}")
            return {'success': False, 'error': str(e)}
