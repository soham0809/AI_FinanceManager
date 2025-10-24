"""
Advanced SMS Classification System
Intelligently classifies and parses different types of financial SMS messages
"""
import re
import json
import requests
from typing import Dict, Any, Optional
from app.config.settings import settings


# Classification keywords for quick identification
UPI_KEYWORDS = [
    'upi', 'vpa', '@ybl', '@okici', '@paytm', '@phonepe', '@googlepay', 
    'upi id', 'upi ref', 'upi transaction', 'bhim', 'gpay'
]

CREDIT_CARD_KEYWORDS = [
    'credit card', 'card ending', 'card no.', 'xxxx', 'card used',
    'cc txn', 'credit', 'mastercard', 'visa', 'rupay'
]

DEBIT_CARD_KEYWORDS = [
    'debit card', 'atm', 'pos', 'card transaction', 'debit',
    'withdrawal', 'dc txn'
]

SUBSCRIPTION_SERVICES = {
    'netflix': ['netflix', 'nflx'],
    'amazon_prime': ['amazon prime', 'prime video', 'amzn prime'],
    'spotify': ['spotify', 'spotify premium'],
    'hotstar': ['hotstar', 'disney+hotstar', 'disney plus'],
    'youtube_premium': ['youtube premium', 'youtube music'],
    'zomato_pro': ['zomato pro', 'zomato gold'],
    'swiggy_super': ['swiggy super', 'swiggy one'],
    'jio': ['jio', 'jio fiber', 'jio prepaid'],
    'airtel': ['airtel', 'airtel postpaid', 'airtel prepaid'],
    'ola': ['ola money', 'ola electric'],
    'uber': ['uber', 'uber eats'],
    'phonepe': ['phonepe wallet'],
    'paytm': ['paytm wallet', 'paytm postpaid']
}

MERCHANT_CATEGORIES = {
    'food_delivery': ['swiggy', 'zomato', 'uber eats', 'foodpanda', 'dominos'],
    'e_commerce': ['amazon', 'flipkart', 'myntra', 'ajio', 'nykaa'],
    'transportation': ['uber', 'ola', 'rapido', 'metro', 'irctc'],
    'fuel': ['indian oil', 'bharat petroleum', 'hp petrol', 'shell'],
    'grocery': ['bigbasket', 'grofers', 'blinkit', 'dunzo', 'zepto'],
    'entertainment': ['bookmyshow', 'paytm movies', 'pvr', 'inox'],
    'utilities': ['electricity', 'gas', 'water', 'broadband', 'mobile'],
    'healthcare': ['apollo', 'max healthcare', '1mg', 'pharmeasy'],
    'education': ['byju', 'unacademy', 'vedantu', 'coursera']
}


def classify_sms_type(sms_text: str) -> str:
    """
    Classifies SMS into specific categories for targeted parsing
    
    Returns: 'UPI', 'CREDIT_CARD', 'DEBIT_CARD', 'SUBSCRIPTION', 'NET_BANKING', or 'OTHER'
    """
    lower_sms = (sms_text or "").lower()
    
    # Check for subscription services first (most specific)
    for service_name, keywords in SUBSCRIPTION_SERVICES.items():
        if any(keyword in lower_sms for keyword in keywords):
            return 'SUBSCRIPTION'
    
    # Check for UPI transactions
    if any(keyword in lower_sms for keyword in UPI_KEYWORDS):
        return 'UPI'
    
    # Check for credit card transactions
    if any(keyword in lower_sms for keyword in CREDIT_CARD_KEYWORDS):
        return 'CREDIT_CARD'
    
    # Check for debit card transactions
    if any(keyword in lower_sms for keyword in DEBIT_CARD_KEYWORDS):
        return 'DEBIT_CARD'
    
    # Check for net banking
    if any(term in lower_sms for term in ['net banking', 'netbanking', 'online transfer', 'neft', 'rtgs', 'imps']):
        return 'NET_BANKING'
    
    return 'OTHER'


def identify_subscription_service(sms_text: str) -> Optional[str]:
    """Identify which subscription service the SMS is about"""
    lower_sms = (sms_text or "").lower()
    
    for service_name, keywords in SUBSCRIPTION_SERVICES.items():
        if any(keyword in lower_sms for keyword in keywords):
            return service_name.replace('_', ' ').title()
    
    return None


def identify_merchant_category(vendor_name: str) -> str:
    """Identify detailed merchant category based on vendor name"""
    lower_vendor = (vendor_name or "").lower()
    
    for category, merchants in MERCHANT_CATEGORIES.items():
        if any(merchant in lower_vendor for merchant in merchants):
            return category.replace('_', ' ').title()
    
    return 'Others'


async def get_ollama_response(prompt: str) -> Dict[str, Any]:
    """Get structured response from Ollama AI"""
    try:
        payload = {
            "model": "llama3.1:latest",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            response_data = response.json()
            llm_response = response_data.get('response', '{}')
            
            # Clean and parse JSON response
            try:
                # Remove markdown formatting if present
                cleaned_response = llm_response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:-3].strip()
                elif cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:-3].strip()
                
                return json.loads(cleaned_response)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {llm_response}")
                return {}
        else:
            print(f"Ollama API error: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"Ollama request error: {e}")
        return {}


async def parse_upi_sms(sms_text: str) -> Dict[str, Any]:
    """Parse UPI SMS with specialized extraction"""
    prompt = f"""
    Extract UPI transaction details from this SMS. Focus on UPI-specific information.
    
    SMS: "{sms_text}"
    
    Return JSON with these fields:
    {{
        "vendor": "merchant/payee name",
        "amount": numeric_amount,
        "upi_transaction_id": "UPI reference number if found",
        "transaction_type": "debit or credit",
        "date": "YYYY-MM-DD format or null",
        "payment_method": "UPI",
        "confidence": confidence_score_0_to_1
    }}
    
    Extract the exact UPI reference number/transaction ID if present.
    """
    
    response = await get_ollama_response(prompt)
    response['payment_method'] = 'UPI'
    
    # Add merchant category
    if 'vendor' in response:
        response['merchant_category'] = identify_merchant_category(response['vendor'])
    
    return response


async def parse_credit_card_sms(sms_text: str) -> Dict[str, Any]:
    """Parse Credit Card SMS with specialized extraction"""
    prompt = f"""
    Extract credit card transaction details from this SMS.
    
    SMS: "{sms_text}"
    
    Return JSON with these fields:
    {{
        "vendor": "merchant name",
        "amount": numeric_amount,
        "card_last_four": "last 4 digits of card or null",
        "transaction_type": "debit or credit",
        "date": "YYYY-MM-DD format or null",
        "payment_method": "Credit Card",
        "confidence": confidence_score_0_to_1
    }}
    
    Look for patterns like 'XXXX1234' or 'ending in 1234' for card numbers.
    """
    
    response = await get_ollama_response(prompt)
    response['payment_method'] = 'Credit Card'
    
    # Add merchant category
    if 'vendor' in response:
        response['merchant_category'] = identify_merchant_category(response['vendor'])
    
    return response


async def parse_debit_card_sms(sms_text: str) -> Dict[str, Any]:
    """Parse Debit Card SMS with specialized extraction"""
    prompt = f"""
    Extract debit card transaction details from this SMS.
    
    SMS: "{sms_text}"
    
    Return JSON with these fields:
    {{
        "vendor": "merchant/ATM name",
        "amount": numeric_amount,
        "card_last_four": "last 4 digits of card or null",
        "transaction_type": "debit",
        "date": "YYYY-MM-DD format or null",
        "payment_method": "Debit Card",
        "confidence": confidence_score_0_to_1
    }}
    
    For ATM withdrawals, set vendor as 'ATM Withdrawal'.
    """
    
    response = await get_ollama_response(prompt)
    response['payment_method'] = 'Debit Card'
    
    # Add merchant category
    if 'vendor' in response:
        response['merchant_category'] = identify_merchant_category(response['vendor'])
    
    return response


async def parse_subscription_sms(sms_text: str) -> Dict[str, Any]:
    """Parse Subscription SMS with specialized extraction"""
    service_name = identify_subscription_service(sms_text)
    
    prompt = f"""
    Extract subscription payment details from this SMS for service: {service_name or 'Unknown'}
    
    SMS: "{sms_text}"
    
    Return JSON with these fields:
    {{
        "vendor": "service name (e.g., Netflix, Amazon Prime)",
        "amount": numeric_amount,
        "subscription_service": "{service_name or 'Unknown'}",
        "is_subscription": true,
        "is_recurring": true,
        "transaction_type": "debit",
        "date": "YYYY-MM-DD format or null",
        "confidence": confidence_score_0_to_1
    }}
    
    This is a subscription payment, so mark it as recurring.
    """
    
    response = await get_ollama_response(prompt)
    response.update({
        'is_subscription': True,
        'is_recurring': True,
        'subscription_service': service_name or response.get('vendor', 'Unknown'),
        'merchant_category': 'Subscription'
    })
    
    return response


async def parse_net_banking_sms(sms_text: str) -> Dict[str, Any]:
    """Parse Net Banking SMS with specialized extraction"""
    prompt = f"""
    Extract net banking transaction details from this SMS.
    
    SMS: "{sms_text}"
    
    Return JSON with these fields:
    {{
        "vendor": "beneficiary/merchant name",
        "amount": numeric_amount,
        "transaction_type": "debit or credit",
        "date": "YYYY-MM-DD format or null",
        "payment_method": "Net Banking",
        "confidence": confidence_score_0_to_1
    }}
    
    Look for NEFT/RTGS/IMPS reference numbers if present.
    """
    
    response = await get_ollama_response(prompt)
    response['payment_method'] = 'Net Banking'
    
    # Add merchant category
    if 'vendor' in response:
        response['merchant_category'] = identify_merchant_category(response['vendor'])
    
    return response


async def classify_and_parse_sms(sms_text: str) -> Dict[str, Any]:
    """
    Main function to classify SMS type and route to appropriate parser
    """
    try:
        # Guard against None or empty SMS
        if not isinstance(sms_text, str) or not sms_text.strip():
            return {
                'success': False,
                'error': 'Empty SMS text',
                'sms_type': 'ERROR'
            }
        # First classify the SMS type
        sms_type = classify_sms_type(sms_text)
        
        # Route to appropriate parser based on classification
        if sms_type == 'UPI':
            return await parse_upi_sms(sms_text)
        elif sms_type == 'CREDIT_CARD':
            return await parse_credit_card_sms(sms_text)
        elif sms_type == 'DEBIT_CARD':
            return await parse_debit_card_sms(sms_text)
        elif sms_type == 'SUBSCRIPTION':
            return await parse_subscription_sms(sms_text)
        elif sms_type == 'NET_BANKING':
            return await parse_net_banking_sms(sms_text)
        else:
            # Fallback to general parsing
            return await parse_general_sms(sms_text)
            
    except Exception as e:
        print(f"SMS classification error: {e}")
        return {
            'success': False,
            'error': f'Classification failed: {str(e)}',
            'sms_type': 'ERROR'
        }


async def parse_general_sms(sms_text: str) -> Dict[str, Any]:
    """Fallback parser for unclassified SMS"""
    prompt = f"""
    Extract basic transaction details from this SMS.
    
    SMS: "{sms_text}"
    
    Return JSON with these fields:
    {{
        "vendor": "merchant/vendor name",
        "amount": numeric_amount,
        "transaction_type": "debit or credit",
        "date": "YYYY-MM-DD format or null",
        "payment_method": "Other",
        "confidence": confidence_score_0_to_1
    }}
    
    If this is not a financial transaction, set confidence to 0.
    """
    
    response = await get_ollama_response(prompt)
    response['payment_method'] = response.get('payment_method', 'Other')
    
    # Add merchant category
    if 'vendor' in response:
        response['merchant_category'] = identify_merchant_category(response['vendor'])
    
    return response
