"""
Gemini AI integration for enhanced financial insights and natural language processing
"""
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiFinancialAssistant:
    """AI-powered financial assistant using Gemini API"""
    
    def __init__(self, api_key: str = "AIzaSyCzL3_QfDj9PKBGGoycG8KqQWiuOEqnAnE"):
        """Initialize Gemini AI with API key"""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.initialized = True
        except Exception as e:
            print(f"Warning: Gemini AI initialization failed: {e}")
            self.model = None
            self.initialized = False
        
    def analyze_spending_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spending patterns using Gemini AI"""
        if not self.initialized:
            return {"success": False, "error": "Gemini AI not initialized"}
            
        try:
            # Prepare transaction data for analysis
            transaction_summary = self._prepare_transaction_summary(transactions)
            
            prompt = f"""
            As a financial advisor AI, analyze the following transaction data and provide insights:
            
            Transaction Summary:
            {transaction_summary}
            
            Please provide:
            1. Key spending patterns and trends
            2. Areas of concern or overspending
            3. Positive financial behaviors
            4. Specific recommendations for improvement
            5. Budget optimization suggestions
            
            Format your response as JSON with the following structure:
            {{
                "patterns": ["pattern1", "pattern2", ...],
                "concerns": ["concern1", "concern2", ...],
                "positive_behaviors": ["behavior1", "behavior2", ...],
                "recommendations": ["rec1", "rec2", ...],
                "budget_suggestions": ["suggestion1", "suggestion2", ...]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                analysis = json.loads(response.text)
                return {
                    'success': True,
                    'analysis': analysis,
                    'generated_at': datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'success': True,
                    'analysis': {
                        'patterns': [response.text[:200] + "..."],
                        'concerns': [],
                        'positive_behaviors': [],
                        'recommendations': [],
                        'budget_suggestions': []
                    },
                    'raw_response': response.text,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in Gemini spending analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }
    
    def get_financial_advice(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized financial advice"""
        if not self.initialized:
            return {"success": False, "error": "Gemini AI not initialized"}
            
        try:
            prompt = f"""
            As a personal financial advisor, provide advice based on this user's financial situation:
            
            User Context:
            - Total Income: ₹{user_data.get('total_income', 0)}
            - Total Spending: ₹{user_data.get('total_spending', 0)}
            - Net Balance: ₹{user_data.get('net_balance', 0)}
            - Top Spending Categories: {user_data.get('top_categories', [])}
            - Monthly Average: ₹{user_data.get('monthly_average', 0)}
            - Financial Goals: {user_data.get('goals', 'Not specified')}
            
            Provide personalized advice in the following areas:
            1. Budgeting strategies
            2. Savings recommendations
            3. Investment suggestions (if applicable)
            4. Expense optimization
            5. Emergency fund planning
            
            Keep advice practical, actionable, and specific to Indian financial context.
            Format as JSON with categories as keys and advice arrays as values.
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                advice = json.loads(response.text)
                return {
                    'success': True,
                    'advice': advice,
                    'generated_at': datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'advice': {'general': [response.text]},
                    'raw_response': response.text,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating financial advice: {e}")
            return {
                'success': False,
                'error': str(e),
                'advice': None
            }
    
    def categorize_transaction_with_ai(self, transaction_text: str, vendor: str) -> Dict[str, Any]:
        """Use AI to categorize transactions more accurately"""
        try:
            prompt = f"""
            Categorize this financial transaction into one of these categories:
            - Food & Dining
            - Shopping
            - Transportation
            - Entertainment
            - Healthcare
            - Education
            - Utilities
            - Fuel
            - Financial
            - Others
            
            Transaction Details:
            - Vendor: {vendor}
            - SMS Text: {transaction_text}
            
            Consider the vendor name and transaction context. Respond with only the category name.
            """
            
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            
            # Validate category
            valid_categories = [
                'Food & Dining', 'Shopping', 'Transportation', 'Entertainment',
                'Healthcare', 'Education', 'Utilities', 'Fuel', 'Financial', 'Others'
            ]
            
            if category not in valid_categories:
                category = 'Others'
            
            return {
                'success': True,
                'category': category,
                'confidence': 0.9  # High confidence for AI categorization
            }
            
        except Exception as e:
            logger.error(f"Error in AI categorization: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': 'Others',
                'confidence': 0.0
            }
    
    def generate_monthly_report(self, transactions: List[Dict[str, Any]], month: str, year: int) -> Dict[str, Any]:
        """Generate comprehensive monthly financial report"""
        if not self.initialized:
            return {"success": False, "error": "Gemini AI not initialized"}
            
        try:
            prompt = f"""
            Generate a comprehensive monthly financial report based on this data:
            
            Monthly Summary:
            - Month: {month} {year}
            - Total Spending: ₹{sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'debit')}
            - Total Income: ₹{sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'credit')}
            - Net Balance: ₹{sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'credit') - sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'debit')}
            - Transaction Count: {len(transactions)}
            - Categories: {self._get_categories(transactions)}
            
            Create a detailed report including:
            1. Executive Summary
            2. Spending Analysis
            3. Category Breakdown
            4. Trends and Patterns
            5. Recommendations for next month
            6. Financial Health Score (1-10)
            
            Format as JSON with clear sections.
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                report = json.loads(response.text)
                return {
                    'success': True,
                    'report': report,
                    'generated_at': datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'report': {'summary': response.text},
                    'raw_response': response.text,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
            return {
                'success': False,
                'error': str(e),
                'report': None
            }
    
    def chat_with_ai(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Chat interface with AI assistant"""
        if not self.initialized:
            return {"success": False, "error": "Gemini AI not initialized"}
            
        try:
            context_str = ""
            if context:
                context_str = f"""
                User's Financial Context:
                - Current Balance: ₹{context.get('balance', 'Unknown')}
                - Monthly Spending: ₹{context.get('monthly_spending', 'Unknown')}
                - Top Categories: {context.get('top_categories', [])}
                """
            
            prompt = f"""
            You are a helpful financial assistant for an Indian user. Answer their question about personal finance.
            
            {context_str}
            
            User Question: {user_message}
            
            Provide a helpful, accurate response. Keep it conversational but informative.
            Focus on practical advice relevant to Indian financial context.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'response': response.text,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in chat response: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': "I'm sorry, I'm having trouble processing your request right now."
            }
    
    def parse_sms_transaction(self, sms_text: str) -> Dict[str, Any]:
        """Use Gemini AI to intelligently parse SMS transaction details"""
        if not self.initialized:
            return {"success": False, "error": "Gemini AI not initialized"}
            
        try:
            prompt = f"""
            Analyze this SMS message to determine if it's a genuine financial transaction or promotional/informational message.
            
            SMS Text: "{sms_text}"
            
            First, determine if this is a REAL TRANSACTION by checking for:
            - Actual money movement (debited/credited/paid/received)
            - Specific amount with currency
            - Account/card information
            - Transaction timestamp
            
            REJECT if it's:
            - Promotional offers (cashback offers, discount coupons)
            - Balance inquiries without transactions
            - OTP/verification messages
            - Account statements or summaries
            - Marketing messages from banks/apps
            - Reward points notifications
            - General alerts or notifications
            
            If it's a REAL TRANSACTION, extract and return ONLY a JSON object:
            {{
                "is_transaction": true,
                "amount": <numeric amount without currency symbol>,
                "vendor": "<merchant/vendor name>",
                "transaction_type": "<debit or credit>",
                "category": "<one of: Food & Dining, Shopping, Transportation, Entertainment, Healthcare, Education, Utilities, Fuel, Financial, Others>",
                "confidence": <confidence score 0.0 to 1.0>,
                "date": "<transaction date in DD-MM-YYYY format from SMS or null if not found>",
                "account_info": "<last 4 digits of account/card or null if not found>",
                "transaction_id": "<UPI ref/transaction ID if available or null>"
            }}
            
            If it's NOT a transaction, return:
            {{
                "is_transaction": false,
                "reason": "<brief reason why it's not a transaction>",
                "confidence": 0.0
            }}
            
            Rules:
            - Be strict about what constitutes a real transaction
            - If amount is not found or unclear, set is_transaction to false
            - Extract transaction_id/UPI ref for duplicate detection
            - Extract the EXACT date from SMS text (look for patterns like "on 15-09-2024", "15/09/2024", "Sep 15, 2024")
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
                        'error': f"Not a transaction: {parsed_data.get('reason', 'Promotional or informational message')}",
                        'raw_response': response.text,
                        'is_promotional': True
                    }
                
                # Validate required fields for transactions
                if parsed_data.get('amount') is None:
                    return {
                        'success': False,
                        'error': 'Could not extract amount from SMS',
                        'raw_response': response.text
                    }
                
                return {
                    'success': True,
                    'transaction_data': parsed_data,
                    'raw_sms': sms_text,
                    'generated_at': datetime.now().isoformat()
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}, Response: {response.text}")
                return {
                    'success': False,
                    'error': f'Failed to parse AI response as JSON: {str(e)}',
                    'raw_response': response.text
                }
                
        except Exception as e:
            logger.error(f"Error in SMS parsing with Gemini: {e}")
            return {
                'success': False,
                'error': str(e),
                'transaction_data': None
            }

    def _prepare_transaction_summary(self, transactions: List[Dict[str, Any]]) -> str:
        """Prepare transaction data for AI analysis"""
        try:
            # Aggregate data
            total_spending = sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'debit')
            total_income = sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'credit')
            
            # Category breakdown
            categories = {}
            for t in transactions:
                if t.get('transaction_type') == 'debit':
                    cat = t.get('category', 'Others')
                    categories[cat] = categories.get(cat, 0) + t.get('amount', 0)
            
            # Top vendors
            vendors = {}
            for t in transactions:
                if t.get('transaction_type') == 'debit':
                    vendor = t.get('vendor', 'Unknown')
                    vendors[vendor] = vendors.get(vendor, 0) + t.get('amount', 0)
            
            top_vendors = sorted(vendors.items(), key=lambda x: x[1], reverse=True)[:5]
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
            
            summary = f"""
            Total Transactions: {len(transactions)}
            Total Spending: ₹{total_spending:.2f}
            Total Income: ₹{total_income:.2f}
            Net Balance: ₹{total_income - total_spending:.2f}
            
            Top Categories:
            {chr(10).join([f"- {cat}: ₹{amount:.2f}" for cat, amount in top_categories])}
            
            Top Vendors:
            {chr(10).join([f"- {vendor}: ₹{amount:.2f}" for vendor, amount in top_vendors])}
            """
            
            return summary
            
        except Exception as e:
            logger.error(f"Error preparing transaction summary: {e}")
            return "Unable to prepare transaction summary"

# Global instance (will be initialized with API key)
gemini_assistant = None

def initialize_gemini(api_key: str):
    """Initialize Gemini assistant with API key"""
    global gemini_assistant
    try:
        gemini_assistant = GeminiFinancialAssistant(api_key)
        logger.info("Gemini AI assistant initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        return False
