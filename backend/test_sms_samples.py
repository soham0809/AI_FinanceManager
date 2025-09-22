"""
Comprehensive test cases for the enhanced SMS parser
Contains real-world SMS samples from Indian banks and UPI providers
"""

from sms_parser import sms_parser

# Real SMS samples from Indian banks and UPI providers
TEST_SMS_SAMPLES = [
    # SBI Bank SMS
    {
        "sms": "Rs 450.00 debited from A/c **1234 on 10-Sep-24 at SWIGGY BANGALORE for UPI/123456789. Avl Bal Rs 15,234.56",
        "expected": {
            "amount": 450.00,
            "vendor": "SWIGGY BANGALORE",
            "type": "debit",
            "category": "Food & Dining"
        }
    },
    
    # HDFC Bank SMS
    {
        "sms": "Thank you for using HDFC Bank NetBanking. You have spent Rs 1,250.50 at AMAZON PAY INDIA on 10-SEP-24. Available balance: Rs 8,765.43",
        "expected": {
            "amount": 1250.50,
            "vendor": "AMAZON PAY INDIA",
            "type": "debit",
            "category": "Shopping"
        }
    },
    
    # ICICI Bank SMS
    {
        "sms": "ICICI Bank: Transaction of Rs 75.00 at UBER TRIP on 10-Sep-24 using Card ending 1234. Current Balance: Rs 12,890.25",
        "expected": {
            "amount": 75.00,
            "vendor": "UBER TRIP",
            "type": "debit",
            "category": "Transportation"
        }
    },
    
    # UPI Credit SMS
    {
        "sms": "You have received Rs 2,000.00 from JOHN DOE via UPI on 10-Sep-24. UPI Ref: 456789123. Available Balance: Rs 14,890.25",
        "expected": {
            "amount": 2000.00,
            "vendor": "JOHN DOE",
            "type": "credit",
            "category": None
        }
    },
    
    # GPay SMS
    {
        "sms": "Paid Rs 299.00 to NETFLIX INDIA via Google Pay. UPI transaction ID: 123456789012345. Balance: Rs 5,432.10",
        "expected": {
            "amount": 299.00,
            "vendor": "NETFLIX INDIA",
            "type": "debit",
            "category": "Entertainment"
        }
    },
    
    # PhonePe SMS
    {
        "sms": "Amount Rs 150.00 paid to APOLLO PHARMACY via PhonePe UPI on 10-Sep-24. Transaction ID: PE987654321. Balance: Rs 3,210.50",
        "expected": {
            "amount": 150.00,
            "vendor": "APOLLO PHARMACY",
            "type": "debit",
            "category": "Healthcare"
        }
    },
    
    # Paytm SMS
    {
        "sms": "Rs 85.00 sent to DUNZO BANGALORE using Paytm UPI. Transaction successful. Ref ID: PT123456789",
        "expected": {
            "amount": 85.00,
            "vendor": "DUNZO BANGALORE",
            "type": "debit",
            "category": "Shopping"
        }
    },
    
    # Fuel Payment
    {
        "sms": "Rs 3,500.00 debited from A/c **5678 on 10-Sep-24 at HP PETROL PUMP for Card transaction. Avl Bal Rs 25,430.75",
        "expected": {
            "amount": 3500.00,
            "vendor": "HP PETROL PUMP",
            "type": "debit",
            "category": "Fuel"
        }
    },
    
    # Education Payment
    {
        "sms": "Payment of Rs 15,000.00 made to BYJU'S CLASSES via UPI on 10-Sep-24. Transaction successful. Balance: Rs 45,230.25",
        "expected": {
            "amount": 15000.00,
            "vendor": "BYJU'S CLASSES",
            "type": "debit",
            "category": "Education"
        }
    },
    
    # Utility Bill
    {
        "sms": "Rs 2,450.00 debited for ELECTRICITY BILL PAYMENT via UPI on 10-Sep-24. Reference: EB123456789. Balance: Rs 18,765.30",
        "expected": {
            "amount": 2450.00,
            "vendor": "ELECTRICITY BILL PAYMENT",
            "type": "debit",
            "category": "Utilities"
        }
    }
]

def test_sms_parser():
    """Test the enhanced SMS parser with real samples"""
    print("Testing Enhanced SMS Parser")
    print("=" * 50)
    
    total_tests = len(TEST_SMS_SAMPLES)
    passed_tests = 0
    
    for i, test_case in enumerate(TEST_SMS_SAMPLES, 1):
        print(f"\nTest {i}/{total_tests}")
        print(f"SMS: {test_case['sms'][:80]}...")
        
        # Parse the SMS
        result = sms_parser.parse_sms(test_case['sms'])
        expected = test_case['expected']
        
        # Check results
        amount_match = abs(result.amount - expected['amount']) < 0.01
        vendor_match = expected['vendor'].lower() in result.vendor.lower()
        type_match = result.transaction_type == expected['type']
        category_match = result.category == expected['category'] or (
            expected['category'] is None and result.category is None
        )
        
        # Print results
        print(f"  Amount: {result.amount} (Expected: {expected['amount']}) {'PASS' if amount_match else 'FAIL'}")
        print(f"  Vendor: {result.vendor} (Expected: {expected['vendor']}) {'PASS' if vendor_match else 'FAIL'}")
        print(f"  Type: {result.transaction_type} (Expected: {expected['type']}) {'PASS' if type_match else 'FAIL'}")
        print(f"  Category: {result.category} (Expected: {expected['category']}) {'PASS' if category_match else 'FAIL'}")
        print(f"  Confidence: {result.confidence:.2f}")
        
        if amount_match and vendor_match and type_match and category_match:
            passed_tests += 1
            print("  Status: PASSED")
        else:
            print("  Status: FAILED")
    
    print(f"\n" + "=" * 50)
    print(f"Test Results: {passed_tests}/{total_tests} passed ({passed_tests/total_tests*100:.1f}%)")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    test_sms_parser()
