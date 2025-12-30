"""Ollama AI integration for intelligent SMS parsing"""
import json
import requests
from typing import Dict, Any, Optional
from app.config.settings import settings


class OllamaAssistant:
    def __init__(self, host: str = None):
        """Initialize Ollama Assistant
        
        Args:
            host: Ollama server URL (default: from settings)
        """
        self.host = host or settings.OLLAMA_HOST
        self.initialized = True  # Assume Ollama is available locally
    
    def parse_sms_transaction(self, sms_text: str) -> Dict[str, Any]:
        """Parse SMS using Ollama AI for intelligent extraction
        
        Args:
            sms_text: SMS message text to parse
            
        Returns:
            Dict containing success status and transaction data or error
        """
        try:
            # Construct detailed prompt for the LLM
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
                "date": "<transaction date in YYYY-MM-DD format from SMS. For 2-digit years like '25', interpret as 2025 (current decade). If no date found, use null>",
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
            - Extract the EXACT date from SMS text and convert to YYYY-MM-DD format
            - If no date found in SMS, set date to null
            - Set high confidence only for clear, unambiguous transactions
            - Return ONLY the JSON object, no additional text
            - Ensure the output is valid JSON format
            """
            
            # Prepare API request payload
            payload = {
                "model": "mistral:7b-instruct-q4_K_M",  # Using the model you mentioned
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            # Make API request to Ollama
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=180  # 3 minute timeout for LLM parsing
            )
            
            # Check response status
            if response.status_code != 200:
                raise requests.exceptions.RequestException(
                    f"Ollama API returned status {response.status_code}: {response.text}"
                )
            
            # Parse the response
            response_data = response.json()
            llm_response = response_data.get('response', '')
            
            # Parse the LLM's JSON response
            try:
                parsed_data = json.loads(llm_response)
            except json.JSONDecodeError as json_err:
                # Try to clean the response if it has extra formatting
                cleaned_response = llm_response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:-3].strip()
                elif cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:-3].strip()
                
                try:
                    parsed_data = json.loads(cleaned_response)
                except json.JSONDecodeError:
                    raise json.JSONDecodeError(
                        f"Failed to parse LLM response as JSON: {llm_response}",
                        llm_response, 0
                    )
            
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
            
        except requests.exceptions.RequestException as req_err:
            print(f"Ollama API request error: {req_err}")
            return {
                'success': False,
                'error': f'Ollama API request failed: {str(req_err)}',
                'is_promotional': False
            }
        
        except json.JSONDecodeError as json_err:
            print(f"JSON decode error: {json_err}")
            return {
                'success': False,
                'error': f'Failed to parse Ollama response: {str(json_err)}',
                'is_promotional': False
            }
        
        except Exception as e:
            print(f"Ollama integration error: {e}")
            return {
                'success': False,
                'error': f'Ollama integration error: {str(e)}',
                'is_promotional': False
            }
    
    def analyze_spending_patterns(self, transactions: list) -> Dict[str, Any]:
        """Analyze spending patterns using Ollama AI
        
        Args:
            transactions: List of transaction objects
            
        Returns:
            Dict containing analysis results
        """
        if not transactions:
            return {'success': False, 'error': 'No transactions provided'}
        
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
            
            Return ONLY the JSON object, no additional text.
            """
            
            payload = {
                "model": "mistral:7b-instruct-q4_K_M",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=120  # 2 minute timeout for analysis
            )
            
            if response.status_code != 200:
                raise requests.exceptions.RequestException(
                    f"Ollama API returned status {response.status_code}"
                )
            
            response_data = response.json()
            llm_response = response_data.get('response', '')
            
            # Clean and parse response
            cleaned_response = llm_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3].strip()
            
            analysis = json.loads(cleaned_response)
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            print(f"Spending analysis error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def generate_response(self, prompt: str, model: str = "mistral:7b-instruct-q4_K_M") -> Dict[str, Any]:
        """Generate a general response using Ollama LLM
        
        Args:
            prompt: The prompt to send to the LLM
            model: The model to use (default: mistral:7b-instruct-q4_K_M)
            
        Returns:
            Dict containing the response or error
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=120  # 2 minute timeout for general responses
            )
            
            if response.status_code != 200:
                raise requests.exceptions.RequestException(
                    f"Ollama API returned status {response.status_code}: {response.text}"
                )
            
            response_data = response.json()
            return {
                'success': True,
                'response': response_data.get('response', ''),
                'model': response_data.get('model', model)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f'Error generating response: {str(e)}'
            }
