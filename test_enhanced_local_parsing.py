#!/usr/bin/env python3
"""
Test Enhanced Local NLP Parsing
Shows improved regex patterns and specific word checking
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.utils.sms_parser import SMSParser

def test_enhanced_parsing():
    """Test the enhanced local parsing capabilities"""
    parser = SMSParser()
    
    print("🚀 Testing Enhanced Local NLP Parsing")
    print("=" * 50)
    
    # Test SMS messages
    test_messages = [
        "Rs.450.00 debited from A/c **1234 on 15-Oct-25 at SWIGGY using UPI",
        "HDFC Bank: Rs.1200 spent at AMAZON RETAIL on 20-10-2025 via Card",
        "UPI payment of Rs.250 to ZOMATO ONLINE via PhonePe on 22-Oct-25",
        "Rs.50 credited to your account from CASHBACK REWARD on 23-Oct-25",
        "Your Jio recharge of Rs.399 was successful on 24-Oct-25",
        "Invalid message without transaction keywords",
        "Rs.5000000 debited - should be rejected for unrealistic amount"
    ]
    
    for i, sms in enumerate(test_messages, 1):
        print(f"\n📱 Test {i}: {sms[:60]}...")
        result = parser.parse_transaction(sms)
        
        if result['success']:
            print(f"✅ SUCCESS")
            print(f"   💰 Amount: ₹{result['amount']}")
            print(f"   🏪 Vendor: {result['vendor']}")
            print(f"   📂 Category: {result['category']}")
            print(f"   📊 Confidence: {result['confidence']:.2f}")
            print(f"   ℹ️  Info: {result.get('parsing_info', 'N/A')}")
            print(f"   🏦 Bank: {result.get('bank', 'Unknown')}")
        else:
            print(f"❌ FAILED: {result['error']}")
    
    print(f"\n🎯 Enhanced Features:")
    print("• More restrictive regex requiring transaction keywords")
    print("• Better vendor extraction with UPI/card patterns")
    print("• Amount validation (₹1 - ₹1,000,000)")
    print("• Enhanced categorization with more keywords")
    print("• Confidence scoring based on extraction quality")
    print("• Parsing info showing '₹amount for vendor'")

if __name__ == "__main__":
    test_enhanced_parsing()
