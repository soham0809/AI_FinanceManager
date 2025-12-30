"""
Test SMS Dataset for AI Finance Manager Evaluation
Contains labeled Indian banking SMS samples for accuracy testing
"""

# Ground truth labels for each SMS
# Format: (sms_text, expected_type, expected_category, expected_amount, expected_vendor)

TEST_SMS_DATASET = [
    # =================== UPI TRANSACTIONS ===================
    # HDFC Bank UPI
    {
        "sms": "Your a/c XXXX1234 debited for Rs.499.00 on 28-12-24. UPI:423456789012. Payee: SWIGGY. Avl bal: Rs.15,432.50-HDFC Bank",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 499.00,
            "vendor": "SWIGGY",
            "is_debit": True
        }
    },
    {
        "sms": "Rs.1,250.00 debited from A/c XX1234 on 27-12-24 via UPI. Ref:423456789013. To:ZOMATO. If not done by you call 18002586161-HDFC Bank",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 1250.00,
            "vendor": "ZOMATO",
            "is_debit": True
        }
    },
    {
        "sms": "Dear Customer, Rs.2,500.00 credited to your a/c XXXX1234 via UPI. Ref:523456789014. From: JOHN DOE. Avl bal: Rs.18,432.50-HDFC Bank",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 2500.00,
            "vendor": "JOHN DOE",
            "is_debit": False
        }
    },
    # SBI UPI
    {
        "sms": "Dear SBI User, your A/c X1234 is debited for Rs.899 on 28Dec24 by UPI ref 423456789015 to AMAZON. Avl Bal Rs.12543.00-SBI",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 899.00,
            "vendor": "AMAZON",
            "is_debit": True
        }
    },
    {
        "sms": "SBI: Rs.350.00 debited from A/c XX1234 on 26Dec24. UPI Ref 423456789016. To: OLA. If not you, call 1800112211-SBI",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 350.00,
            "vendor": "OLA",
            "is_debit": True
        }
    },
    # ICICI Bank UPI
    {
        "sms": "ICICI Bank Acct XX123 debited with Rs.1,599.00 on 28-Dec-24. UPI:423456789017. FLIPKART. Call 18002662 if not done by you.",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 1599.00,
            "vendor": "FLIPKART",
            "is_debit": True
        }
    },
    {
        "sms": "Rs.799.00 debited from ICICI Bank AC XX123 on 27Dec via UPI. Ref 423456789018. To: UBER. Bal: Rs.8,234.00",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 799.00,
            "vendor": "UBER",
            "is_debit": True
        }
    },
    # Axis Bank UPI
    {
        "sms": "Axis Bank: Rs.2,999.00 debited from a/c XX4567 via UPI on 28-12-2024. Ref: 423456789019. To: MYNTRA. Bal: Rs.5,678.00",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 2999.00,
            "vendor": "MYNTRA",
            "is_debit": True
        }
    },
    # Kotak UPI
    {
        "sms": "Kotak: A/c X6789 debited Rs.450.00 on 26Dec for UPI txn to RAPIDO. Ref:423456789020. Bal Rs.3,456.00",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 450.00,
            "vendor": "RAPIDO",
            "is_debit": True
        }
    },
    # PhonePe/GPay specific
    {
        "sms": "Rs.199.00 sent to CHAI POINT via PhonePe. UPI Ref: 423456789021. Check balance at phonepe.com",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 199.00,
            "vendor": "CHAI POINT",
            "is_debit": True
        }
    },
    {
        "sms": "Money sent! Rs.1,500.00 to BIGBASKET via Google Pay. UPI ID: bigbasket@ybl. Ref: 423456789022",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 1500.00,
            "vendor": "BIGBASKET",
            "is_debit": True
        }
    },
    
    # =================== CREDIT CARD TRANSACTIONS ===================
    {
        "sms": "Thank you for using your HDFC Bank Credit Card ending 5678 for Rs.4,999.00 at CROMA on 28-12-24. Avl Limit: Rs.85,000.00",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 4999.00,
            "vendor": "CROMA",
            "is_debit": True
        }
    },
    {
        "sms": "Alert: Your ICICI Credit Card XX9876 is used for Rs.12,500.00 at VIJAY SALES on 27Dec24. SMS BLOCK to 9215676766 if not you.",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 12500.00,
            "vendor": "VIJAY SALES",
            "is_debit": True
        }
    },
    {
        "sms": "SBI Card ending 4321 used for Rs.3,499.00 at NYKAA.COM on 26-12-2024. Available limit: Rs.42,500.00",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 3499.00,
            "vendor": "NYKAA.COM",
            "is_debit": True
        }
    },
    {
        "sms": "Your Axis Bank Credit Card XX1111 has been charged Rs.8,999.00 at TANISHQ on 28Dec24. Limit Avl: Rs.61,000.00",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 8999.00,
            "vendor": "TANISHQ",
            "is_debit": True
        }
    },
    {
        "sms": "Kotak Credit Card XX2222 used for Rs.1,850.00 at PVR CINEMAS on 27-12-24. Call 1860 266 2666 if not done by you.",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Entertainment",
            "amount": 1850.00,
            "vendor": "PVR CINEMAS",
            "is_debit": True
        }
    },
    {
        "sms": "AMEX Card ending 3333 charged Rs.25,000.00 at APPLE STORE on 28Dec24. Check limit on Amex app.",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 25000.00,
            "vendor": "APPLE STORE",
            "is_debit": True
        }
    },
    {
        "sms": "Transaction alert: RBL Credit Card XX4444 used for Rs.599.00 at DOMINOS on 26Dec24. Reply STOP to opt out.",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Food & Dining",
            "amount": 599.00,
            "vendor": "DOMINOS",
            "is_debit": True
        }
    },
    
    # =================== DEBIT CARD TRANSACTIONS ===================
    {
        "sms": "Your Debit Card XX5678 is used for Rs.2,350.00 at DECATHLON on 28-12-24 via POS. Avl Bal: Rs.15,432.00-HDFC Bank",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Shopping",
            "amount": 2350.00,
            "vendor": "DECATHLON",
            "is_debit": True
        }
    },
    {
        "sms": "SBI Debit Card XX9012 used for Rs.890.00 at RELIANCE FRESH on 27Dec24. Bal: Rs.8,765.00. Call 1800112211 if not you.",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Shopping",
            "amount": 890.00,
            "vendor": "RELIANCE FRESH",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI Debit Card XX3456 debited Rs.1,250.00 at APOLLO PHARMACY on 26Dec24. Bal Rs.4,321.00",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Healthcare",
            "amount": 1250.00,
            "vendor": "APOLLO PHARMACY",
            "is_debit": True
        }
    },
    {
        "sms": "ATM withdrawal Rs.5,000.00 from your HDFC Debit Card XX7890 at HDFC ATM ANDHERI on 28-12-24. Bal: Rs.25,000.00",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Cash Withdrawal",
            "amount": 5000.00,
            "vendor": "HDFC ATM ANDHERI",
            "is_debit": True
        }
    },
    
    # =================== SUBSCRIPTION TRANSACTIONS ===================
    {
        "sms": "Your subscription of Rs.199 for NETFLIX has been renewed successfully on 28-12-24. Next billing date: 28-01-25.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 199.00,
            "vendor": "NETFLIX",
            "is_debit": True
        }
    },
    {
        "sms": "SPOTIFY Premium subscription Rs.119 auto-renewed on 27Dec24. Manage at spotify.com/account",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 119.00,
            "vendor": "SPOTIFY",
            "is_debit": True
        }
    },
    {
        "sms": "Amazon Prime membership Rs.1,499 renewed for 1 year on 26-12-24. Valid till 26-12-25.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Shopping",
            "amount": 1499.00,
            "vendor": "AMAZON PRIME",
            "is_debit": True
        }
    },
    {
        "sms": "Your HOTSTAR subscription of Rs.299/month renewed on 28Dec24. Enjoy unlimited streaming!",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 299.00,
            "vendor": "HOTSTAR",
            "is_debit": True
        }
    },
    {
        "sms": "YOUTUBE Premium Rs.129 monthly subscription renewed. Next billing: 28-01-25. Manage at youtube.com/paid_memberships",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 129.00,
            "vendor": "YOUTUBE PREMIUM",
            "is_debit": True
        }
    },
    {
        "sms": "Your JIO Postpaid bill of Rs.599 is due on 05-Jan-25. Pay now via MyJio app or jio.com",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Utilities",
            "amount": 599.00,
            "vendor": "JIO",
            "is_debit": True
        }
    },
    {
        "sms": "AIRTEL: Your postpaid bill of Rs.749 for Dec'24 is generated. Due date: 10-Jan-25. Pay via Airtel Thanks app.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Utilities",
            "amount": 749.00,
            "vendor": "AIRTEL",
            "is_debit": True
        }
    },
    {
        "sms": "Your LINKEDIN Premium subscription Rs.1,599/month renewed on 27Dec24. Access exclusive features.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Education",
            "amount": 1599.00,
            "vendor": "LINKEDIN PREMIUM",
            "is_debit": True
        }
    },
    
    # =================== NET BANKING TRANSACTIONS ===================
    {
        "sms": "Rs.15,000.00 transferred from your HDFC a/c XX1234 to LANDLORD via NEFT on 28-12-24. Ref: HDFC123456789. Bal: Rs.35,000.00",
        "expected": {
            "type": "NET_BANKING",
            "category": "Rent",
            "amount": 15000.00,
            "vendor": "LANDLORD",
            "is_debit": True
        }
    },
    {
        "sms": "IMPS of Rs.5,000.00 from your SBI a/c to ELECTRICITY BOARD successful. Ref: SBI987654321. Bal Rs.12,345.00",
        "expected": {
            "type": "NET_BANKING",
            "category": "Utilities",
            "amount": 5000.00,
            "vendor": "ELECTRICITY BOARD",
            "is_debit": True
        }
    },
    {
        "sms": "RTGS Rs.50,000.00 credited to your ICICI a/c XX5678 from XYZ COMPANY on 27Dec24. Ref: ICICI456789123",
        "expected": {
            "type": "NET_BANKING",
            "category": "Income",
            "amount": 50000.00,
            "vendor": "XYZ COMPANY",
            "is_debit": False
        }
    },
    {
        "sms": "NEFT of Rs.2,500.00 debited from Axis a/c XX9012 to GAS AGENCY. Ref AXIS789012345. Bal Rs.8,765.00",
        "expected": {
            "type": "NET_BANKING",
            "category": "Utilities",
            "amount": 2500.00,
            "vendor": "GAS AGENCY",
            "is_debit": True
        }
    },
    
    # =================== WALLET TRANSACTIONS ===================
    {
        "sms": "Rs.500.00 added to your PAYTM Wallet. Txn ID: PAY123456789. New balance: Rs.1,234.00",
        "expected": {
            "type": "UPI",
            "category": "Wallet Top-up",
            "amount": 500.00,
            "vendor": "PAYTM WALLET",
            "is_debit": False
        }
    },
    {
        "sms": "PHONEPE: Rs.200.00 paid to METRO RECHARGE. Wallet Bal: Rs.345.00. Txn ID: PHN987654321",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 200.00,
            "vendor": "METRO RECHARGE",
            "is_debit": True
        }
    },
    
    # =================== FOOD DELIVERY SPECIFIC ===================
    {
        "sms": "Order confirmed! Your SWIGGY order #SW123456 of Rs.458.00 will arrive by 8:30 PM. Track at swiggy.com/track",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 458.00,
            "vendor": "SWIGGY",
            "is_debit": True
        }
    },
    {
        "sms": "ZOMATO: Your order #ZMT789012 worth Rs.672.00 is on the way! Delivery by 9:15 PM.",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 672.00,
            "vendor": "ZOMATO",
            "is_debit": True
        }
    },
    
    # =================== E-COMMERCE SPECIFIC ===================
    {
        "sms": "AMAZON: Your order #402-1234567-8901234 for Rs.2,499.00 has been shipped. Delivery by 30-Dec-24.",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 2499.00,
            "vendor": "AMAZON",
            "is_debit": True
        }
    },
    {
        "sms": "FLIPKART: Order #OD123456789012 confirmed! Rs.1,899.00. Expected delivery: 29-Dec-24.",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 1899.00,
            "vendor": "FLIPKART",
            "is_debit": True
        }
    },
    
    # =================== UTILITY BILLS ===================
    {
        "sms": "TATA POWER: Your electricity bill of Rs.2,345.00 for Dec'24 is generated. Due date: 15-Jan-25. Pay via TATA Power app.",
        "expected": {
            "type": "OTHER",
            "category": "Utilities",
            "amount": 2345.00,
            "vendor": "TATA POWER",
            "is_debit": True
        }
    },
    {
        "sms": "MAHANAGAR GAS: Your gas bill of Rs.890.00 for Dec'24 is ready. Pay before 10-Jan-25 to avoid late fee.",
        "expected": {
            "type": "OTHER",
            "category": "Utilities",
            "amount": 890.00,
            "vendor": "MAHANAGAR GAS",
            "is_debit": True
        }
    },
    
    # =================== HEALTHCARE ===================
    {
        "sms": "Thank you for visiting APOLLO HOSPITALS. Your consultation fee of Rs.800.00 has been received. Report ID: APL123456",
        "expected": {
            "type": "OTHER",
            "category": "Healthcare",
            "amount": 800.00,
            "vendor": "APOLLO HOSPITALS",
            "is_debit": True
        }
    },
    {
        "sms": "1MG: Your order #1MG789012 for Rs.456.00 has been dispatched. Delivery by 29-Dec-24.",
        "expected": {
            "type": "OTHER",
            "category": "Healthcare",
            "amount": 456.00,
            "vendor": "1MG",
            "is_debit": True
        }
    },
    
    # =================== TRAVEL ===================
    {
        "sms": "IRCTC: Your ticket PNR 1234567890 for MUMBAI-DELHI on 02-Jan-25 is confirmed. Fare: Rs.2,150.00",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 2150.00,
            "vendor": "IRCTC",
            "is_debit": True
        }
    },
    {
        "sms": "MAKEMYTRIP: Your flight booking #MMT123456 for Rs.5,678.00 is confirmed. Travel date: 05-Jan-25.",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 5678.00,
            "vendor": "MAKEMYTRIP",
            "is_debit": True
        }
    },
    
    # =================== EDUCATION ===================
    {
        "sms": "BYJU'S: Your subscription of Rs.12,999 for Class 10 package activated. Valid for 1 year.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Education",
            "amount": 12999.00,
            "vendor": "BYJU'S",
            "is_debit": True
        }
    },
    {
        "sms": "UNACADEMY: Your Plus subscription of Rs.999/month renewed. Access all courses at unacademy.com",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Education",
            "amount": 999.00,
            "vendor": "UNACADEMY",
            "is_debit": True
        }
    },
    
    # =================== EDGE CASES ===================
    # Amount with spaces
    {
        "sms": "Rs 1,23,456.78 credited to your a/c XXXX1234 via NEFT. Ref: HDFC999888777. Bal: Rs 2,34,567.89-HDFC Bank",
        "expected": {
            "type": "NET_BANKING",
            "category": "Income",
            "amount": 123456.78,
            "vendor": "NEFT TRANSFER",
            "is_debit": False
        }
    },
    # INR format
    {
        "sms": "INR 999.00 debited from your ICICI a/c XX1234 for UPI txn to STARBUCKS. Ref: 123456789012",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 999.00,
            "vendor": "STARBUCKS",
            "is_debit": True
        }
    },
    # No comma in amount
    {
        "sms": "SBI: Rs.50000 credited to your a/c XX5678 from PARENT on 28Dec24. Your Bal is Rs.75000",
        "expected": {
            "type": "NET_BANKING",
            "category": "Income",
            "amount": 50000.00,
            "vendor": "PARENT",
            "is_debit": False
        }
    },
    
    # =================== HARD EDGE CASES ===================
    
    # Regional/Lesser-known banks
    {
        "sms": "PUNJAB NATIONAL BANK: Rs.1234.56 debited from your a/c for UPI payment to KIRANA STORE. Ref:PNB123456",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 1234.56,
            "vendor": "KIRANA STORE",
            "is_debit": True
        }
    },
    {
        "sms": "BANK OF BARODA Alert: INR 567.00 transferred to ELECTRICIAN via UPI. Txn Ref BOB789012",
        "expected": {
            "type": "UPI",
            "category": "Services",
            "amount": 567.00,
            "vendor": "ELECTRICIAN",
            "is_debit": True
        }
    },
    {
        "sms": "CANARA BANK: Your a/c XX7890 is debited INR 2345.00 towards UPI/P2M/MER123456. Avl Bal: 15000.00",
        "expected": {
            "type": "UPI",
            "category": "Other",
            "amount": 2345.00,
            "vendor": "MER123456",
            "is_debit": True
        }
    },
    {
        "sms": "UNION BANK: A/c X5678 debited by Rs.890/- on 28Dec for NEFT to RENT. Bal INR 12345",
        "expected": {
            "type": "NET_BANKING",
            "category": "Rent",
            "amount": 890.00,
            "vendor": "RENT",
            "is_debit": True
        }
    },
    {
        "sms": "IDBI Bank: Rs 4,567 debited from Ac ending 1234 via UPI. To: MILKMAN. Ref: IDBI456789",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 4567.00,
            "vendor": "MILKMAN",
            "is_debit": True
        }
    },
    
    # Unusual amount formats
    {
        "sms": "Amt Rs. 12,34,567.89 credited to your HDFC a/c via RTGS from SALARY ACCOUNT. Ref RTGS999",
        "expected": {
            "type": "NET_BANKING",
            "category": "Income",
            "amount": 1234567.89,
            "vendor": "SALARY ACCOUNT",
            "is_debit": False
        }
    },
    {
        "sms": "You've received ₹50,000 in your Paytm wallet from FRIEND. Bal: ₹52,345",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 50000.00,
            "vendor": "FRIEND",
            "is_debit": False
        }
    },
    {
        "sms": "Payment of Rs0.01 received from UPI ID test@ybl for testing purpose",
        "expected": {
            "type": "UPI",
            "category": "Other",
            "amount": 0.01,
            "vendor": "test@ybl",
            "is_debit": False
        }
    },
    {
        "sms": "Dear Customer, INR 99,999 debited fr A/c 1234 by ATM at UNKNOWN LOCATION. Bal: 5000",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Cash Withdrawal",
            "amount": 99999.00,
            "vendor": "ATM UNKNOWN LOCATION",
            "is_debit": True
        }
    },
    
    # Truncated/Incomplete SMS
    {
        "sms": "HDFC: Rs.2500 deb fr ac XX12 UPI SWIGGY Re",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 2500.00,
            "vendor": "SWIGGY",
            "is_debit": True
        }
    },
    {
        "sms": "SBI CC XX4321 used Rs.15000 AMAZON",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 15000.00,
            "vendor": "AMAZON",
            "is_debit": True
        }
    },
    
    # SMS with special characters and emojis
    {
        "sms": "🎉 Congrats! Rs.10,000 cashback credited to your a/c XXXX1234. Shop more & earn more! 🛒",
        "expected": {
            "type": "OTHER",
            "category": "Cashback",
            "amount": 10000.00,
            "vendor": "CASHBACK",
            "is_debit": False
        }
    },
    {
        "sms": "⚠️ ALERT: Rs.5,678.00 debited from your a/c XX1234 at SUSPICIOUS MERCHANT. If not you, call 1800XXXXXX ⚠️",
        "expected": {
            "type": "OTHER",
            "category": "Other",
            "amount": 5678.00,
            "vendor": "SUSPICIOUS MERCHANT",
            "is_debit": True
        }
    },
    
    # Mixed language (Hindi-English)
    {
        "sms": "Aapke HDFC a/c se Rs.999 UPI dwara DMART ko transfer hua. Shesh rashi: Rs.5000",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 999.00,
            "vendor": "DMART",
            "is_debit": True
        }
    },
    {
        "sms": "SBI: Aapke khate mein Rs.25000 NEFT se jama hua EMPLOYER se. Balance: Rs.30000",
        "expected": {
            "type": "NET_BANKING",
            "category": "Income",
            "amount": 25000.00,
            "vendor": "EMPLOYER",
            "is_debit": False
        }
    },
    
    # Failed transactions
    {
        "sms": "Transaction FAILED: Rs.1,500 to MERCHANT via UPI. Amount NOT debited. Ref:FAIL123456",
        "expected": {
            "type": "UPI",
            "category": "Failed",
            "amount": 1500.00,
            "vendor": "MERCHANT",
            "is_debit": False
        }
    },
    {
        "sms": "Your payment of Rs.2999 to FLIPKART was unsuccessful. Please retry. Error: Insufficient funds",
        "expected": {
            "type": "OTHER",
            "category": "Failed",
            "amount": 2999.00,
            "vendor": "FLIPKART",
            "is_debit": False
        }
    },
    
    # Refund messages
    {
        "sms": "REFUND: Rs.1,299.00 credited to your a/c XX1234 for order #AMZ987654. Original payment reversed.",
        "expected": {
            "type": "OTHER",
            "category": "Refund",
            "amount": 1299.00,
            "vendor": "AMAZON REFUND",
            "is_debit": False
        }
    },
    {
        "sms": "Swiggy refund of Rs.450 processed successfully to your bank account. Takes 3-5 days.",
        "expected": {
            "type": "OTHER",
            "category": "Refund",
            "amount": 450.00,
            "vendor": "SWIGGY REFUND",
            "is_debit": False
        }
    },
    
    # EMI/Loan messages
    {
        "sms": "HDFC Bank: EMI of Rs.12,500 for Loan A/c XX9876 debited from your savings a/c. 23/48 EMIs paid.",
        "expected": {
            "type": "NET_BANKING",
            "category": "EMI",
            "amount": 12500.00,
            "vendor": "HDFC LOAN EMI",
            "is_debit": True
        }
    },
    {
        "sms": "Bajaj Finserv: Your EMI of Rs.8,999 for XX1234 is due on 05-Jan-25. Pay now to avoid late fee.",
        "expected": {
            "type": "OTHER",
            "category": "EMI",
            "amount": 8999.00,
            "vendor": "BAJAJ FINSERV",
            "is_debit": True
        }
    },
    {
        "sms": "CREDIT CARD EMI: Rs.3,333 billed on HDFC CC XX5678 for purchase at ONEPLUS. 1/6 EMIs.",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "EMI",
            "amount": 3333.00,
            "vendor": "ONEPLUS EMI",
            "is_debit": True
        }
    },
    
    # International transactions
    {
        "sms": "ICICI CC XX1234: USD 49.99 (approx INR 4,199) charged at SPOTIFY SWEDEN. Forex markup applied.",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Entertainment",
            "amount": 4199.00,
            "vendor": "SPOTIFY SWEDEN",
            "is_debit": True
        }
    },
    {
        "sms": "Foreign txn: Rs.8,500 debited for USD 99.00 at AMAZON.COM US. Card: XX9876",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 8500.00,
            "vendor": "AMAZON.COM US",
            "is_debit": True
        }
    },
    
    # Very long vendor names
    {
        "sms": "UPI: Rs.1500 paid to MUMBAI CENTRAL RAILWAY STATION FOOD COURT STALL NUMBER 23. Ref: 123456789012",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 1500.00,
            "vendor": "MUMBAI CENTRAL RAILWAY STATION FOOD COURT",
            "is_debit": True
        }
    },
    {
        "sms": "Rs.999 debited via UPI to SHRI GANESH TRADING COMPANY AND WHOLESALE DISTRIBUTORS. Bal: 5000",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 999.00,
            "vendor": "SHRI GANESH TRADING COMPANY",
            "is_debit": True
        }
    },
    
    # Ambiguous payment types
    {
        "sms": "Payment successful! Rs.2,500 sent to 9876543210. Have a great day!",
        "expected": {
            "type": "UPI",
            "category": "Transfer",
            "amount": 2500.00,
            "vendor": "9876543210",
            "is_debit": True
        }
    },
    {
        "sms": "Rs.500 transferred successfully. Thank you for using our services.",
        "expected": {
            "type": "OTHER",
            "category": "Transfer",
            "amount": 500.00,
            "vendor": "UNKNOWN",
            "is_debit": True
        }
    },
    
    # Insurance/Investment
    {
        "sms": "LIC: Premium of Rs.15,000 for Policy 12345678 debited from your a/c. Next due: 28-Mar-25.",
        "expected": {
            "type": "NET_BANKING",
            "category": "Insurance",
            "amount": 15000.00,
            "vendor": "LIC",
            "is_debit": True
        }
    },
    {
        "sms": "SIP: Rs.5,000 invested in HDFC EQUITY FUND via SIP. Units allotted: 45.67. NAV: 109.45",
        "expected": {
            "type": "NET_BANKING",
            "category": "Investment",
            "amount": 5000.00,
            "vendor": "HDFC MUTUAL FUND",
            "is_debit": True
        }
    },
    {
        "sms": "ZERODHA: Rs.10,000 added to your trading account. Available margin: Rs.15,000",
        "expected": {
            "type": "NET_BANKING",
            "category": "Investment",
            "amount": 10000.00,
            "vendor": "ZERODHA",
            "is_debit": True
        }
    },
    
    # Multiple amounts in SMS (tricky)
    {
        "sms": "HDFC: Rs.500 debited. Prev Bal: Rs.10,000. New Bal: Rs.9,500. Txn to MERCHANT.",
        "expected": {
            "type": "OTHER",
            "category": "Other",
            "amount": 500.00,
            "vendor": "MERCHANT",
            "is_debit": True
        }
    },
    {
        "sms": "Bill Rs.2,345. Cashback Rs.100. Final paid Rs.2,245 via UPI to DMART.",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 2245.00,
            "vendor": "DMART",
            "is_debit": True
        }
    },
    
    # Government/Utility
    {
        "sms": "UIDAI: Aadhaar auth success for HDFC Bank. Rs.0 charged. Ref: ADH123456789012",
        "expected": {
            "type": "OTHER",
            "category": "Authentication",
            "amount": 0.00,
            "vendor": "UIDAI AADHAAR",
            "is_debit": False
        }
    },
    {
        "sms": "BBMP: Property tax of Rs.5,678 paid successfully. Receipt: BBMP/2024/123456",
        "expected": {
            "type": "NET_BANKING",
            "category": "Government",
            "amount": 5678.00,
            "vendor": "BBMP PROPERTY TAX",
            "is_debit": True
        }
    },
    {
        "sms": "RTO: Vehicle registration fee Rs.2,500 received for KA01MX1234. Ref: RTO789012",
        "expected": {
            "type": "NET_BANKING",
            "category": "Government",
            "amount": 2500.00,
            "vendor": "RTO",
            "is_debit": True
        }
    },
    
    # Gaming/In-app purchases
    {
        "sms": "GPAY: Rs.99 paid to PUBG MOBILE for in-app purchase. UPI Ref: 123456789012",
        "expected": {
            "type": "UPI",
            "category": "Gaming",
            "amount": 99.00,
            "vendor": "PUBG MOBILE",
            "is_debit": True
        }
    },
    {
        "sms": "Apple iTunes: Rs.799 charged on ICICI CC for App Store purchase. Ref: APPLE123",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Entertainment",
            "amount": 799.00,
            "vendor": "APPLE ITUNES",
            "is_debit": True
        }
    },
    
    # Crypto/Modern fintech
    {
        "sms": "COINSWITCH: Rs.10,000 deposited to your account. Buy crypto now!",
        "expected": {
            "type": "OTHER",
            "category": "Investment",
            "amount": 10000.00,
            "vendor": "COINSWITCH",
            "is_debit": True
        }
    },
    {
        "sms": "CRED: Rs.5,000 paid towards HDFC CC bill. Earned 5000 CRED coins! 🎉",
        "expected": {
            "type": "OTHER",
            "category": "Credit Card Payment",
            "amount": 5000.00,
            "vendor": "CRED",
            "is_debit": True
        }
    },
    
    # Very old date formats
    {
        "sms": "HDFC: Rs.1234 debited on 01/12/24 via UPI to SHOP. Ref: 123456789012",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 1234.00,
            "vendor": "SHOP",
            "is_debit": True
        }
    },
    {
        "sms": "SBI Alert 25-Dec-2024 10:30:45: Rs.999 sent to GIFT SHOP via UPI",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 999.00,
            "vendor": "GIFT SHOP",
            "is_debit": True
        }
    },
    
    # =================== REAL-WORLD SBI SMS (User Provided) ===================
    {
        "sms": "Dear SBI User, your A/c X7151-credited by Rs.150 on 19Sep25 transfer from Mr. OMKAR UDAY PARADE Ref No 526215189839 -SBI",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 150.00,
            "vendor": "Mr. OMKAR UDAY PARADE",
            "is_debit": False
        }
    },
    {
        "sms": "Dear SBI User, your A/c X7151-credited by Rs.20000 on 21Sep25 transfer from SAYALI SANJAY JOSHI Ref No 526417967986 -SBI",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 20000.00,
            "vendor": "SAYALI SANJAY JOSHI",
            "is_debit": False
        }
    },
    {
        "sms": "Dear UPI user A/C X7151 debited by 5.0 on date 24Sep25 trf to Indian Railways Refno 526784613583 If not u? call-1800111109 for other services-18001234-SBI",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 5.00,
            "vendor": "Indian Railways",
            "is_debit": True
        }
    },
    {
        "sms": "Dear UPI user A/C X7151 debited by 20.0 on date 04Oct25 trf to Indian Railways Refno 527775139747 If not u? call-1800111109 for other services-18001234-SBI",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 20.00,
            "vendor": "Indian Railways",
            "is_debit": True
        }
    },
    {
        "sms": "Dear UPI user A/C X8724 debited by 437.0 on date 25Oct25 trf to Mr OMKAR UDAY PA Refno 391304219631 If not u? call-1800111109 for other services-18001234-SBI",
        "expected": {
            "type": "UPI",
            "category": "Transfer",
            "amount": 437.00,
            "vendor": "Mr OMKAR UDAY PA",
            "is_debit": True
        }
    },
    {
        "sms": "Dear UPI user A/C X7151 debited by 80.0 on date 31Oct25 trf to Gautham N Nair Refno 567010350294 If not u? call-1800111109 for other services-18001234-SBI",
        "expected": {
            "type": "UPI",
            "category": "Transfer",
            "amount": 80.00,
            "vendor": "Gautham N Nair",
            "is_debit": True
        }
    },
    {
        "sms": "Dear UPI user A/C X7151 debited by 500.0 on date 31Oct25 trf to pratyushajoshi07 Refno 567038335419 If not u? call-1800111109 for other services-18001234-SBI",
        "expected": {
            "type": "UPI",
            "category": "Transfer",
            "amount": 500.00,
            "vendor": "pratyushajoshi07",
            "is_debit": True
        }
    },
    {
        "sms": "Dear UPI user A/C X7151 debited by 100.0 on date 20Jun25 trf to BHAVANI SUPER MA Refno 553770010416. If not u? call 1800111109. -SBI",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 100.00,
            "vendor": "BHAVANI SUPER MA",
            "is_debit": True
        }
    },
    {
        "sms": "Dear SBI User, your A/c X7151-credited by Rs.7000 on 09Sep25 transfer from SAYALI SANJAY JOSHI Ref No 525287739800 -SBI",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 7000.00,
            "vendor": "SAYALI SANJAY JOSHI",
            "is_debit": False
        }
    },
    
    # =================== NO_TRANSACTION: UPI MANDATE (Not actual transactions) ===================
    {
        "sms": "Your UPI-Mandate is successfully cancelled towards YouTube for 149.00 from A/c No.XXXXXX7151. UMN:3f06172bc057af3ee063c1d4bf0a51d9@oksbi -SBI",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "UPI Mandate Cancelled",
            "amount": 149.00,
            "vendor": "YouTube",
            "is_debit": False
        }
    },
    {
        "sms": "Your UPI-Mandate for Rs.399.00 is successfully created towards OpenAI LLC from A/c No: XXXXXX7151. UMN:42be05137ff499c3e0630c2eb00a5010@oksbi. If not you, kindly report on 18001234. -SBI",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "UPI Mandate Created",
            "amount": 399.00,
            "vendor": "OpenAI LLC",
            "is_debit": False
        }
    },
    {
        "sms": "Your UPI-Mandate for Rs.15000.00 is successfully created towards Google Cloud from A/c No: XXXXXX7151. UMN:42de8c036e03ce03e063a4d7bf0a8e2a@oksbi. If not you, kindly report on 18001234. -SBI",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "UPI Mandate Created",
            "amount": 15000.00,
            "vendor": "Google Cloud",
            "is_debit": False
        }
    },
    {
        "sms": "Your UPI-Mandate for Rs.399.00 is successfully created towards APPLE MEDIA SERVICES from A/c No: XXXXXX7151. UMN:44ddf017a4663d4ae063a4d7bf0aa16c@oksbi. If not you, kindly report on 18001234. -SBI",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "UPI Mandate Created",
            "amount": 399.00,
            "vendor": "APPLE MEDIA SERVICES",
            "is_debit": False
        }
    },
    {
        "sms": "Your UPI-Mandate for Rs.139.00 is successfully created towards SPOTIFY INDIA PVT LTD from A/c No: XXXXXX7151. UMN:4667957d79f786fee06373d6bf0a73ae@oksbi. If not you, kindly report on 18001234. -SBI",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "UPI Mandate Created",
            "amount": 139.00,
            "vendor": "SPOTIFY INDIA PVT LTD",
            "is_debit": False
        }
    },
    
    # =================== NO_TRANSACTION: PROMOTIONAL SMS ===================
    {
        "sms": "Aapka Airtel Prepaid pack 8793XXX302 par samapt hone wala hai! Rs349 se recharge karein aur niche diye gaye labh ka aanand le 28 dino tak. 1. Unlimited 5G data + 2GB/din 2. Unlimited call",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Airtel",
            "is_debit": False
        }
    },
    {
        "sms": "Aapka Airtel Prepaid pack 8793XXX302 par samapt ho gaya hai! Rs349 se recharge karein aur niche diye gaye labh ka aanand le 28 dino tak.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Airtel",
            "is_debit": False
        }
    },
    {
        "sms": "Alert!100%-: of your daily high speed data is consumed. Get 12GB data topup at just Rs161 | valid for 30 days. Recharge now i.airtel.in/dtpck",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Airtel",
            "is_debit": False
        }
    },
    {
        "sms": "Alert!100%-: of your daily high speed data is consumed. Get 15GB data topup at just Rs181 | valid for 30 days. Recharge now i.airtel.in/dtpck",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Airtel",
            "is_debit": False
        }
    },
    {
        "sms": "9594940316 par sabhi sewayein band hain kyuki aapne recharge nahi kia hai. Sewa shuru karein ke lie recharge karein i.airtel.in/FDPNew Ignore if recharged",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Airtel",
            "is_debit": False
        }
    },
    
    # =================== NO_TRANSACTION: DELIVERY/OTP/NON-FINANCIAL ===================
    {
        "sms": "Your order with Blue Dart AWB# 82157472736 was delivered to SOHAM . Please Rate our Service on https://acl.cc/BLUDRT/qlgBXP3X",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Delivery Notification",
            "amount": 0.00,
            "vendor": "Blue Dart",
            "is_debit": False
        }
    },
    {
        "sms": "Your OTP for login is 123456. Valid for 5 minutes. Do not share with anyone.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "OTP",
            "amount": 0.00,
            "vendor": "Unknown",
            "is_debit": False
        }
    },
    {
        "sms": "Thank you for shopping at Reliance Fresh. Visit again!",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Reliance Fresh",
            "is_debit": False
        }
    },
    
    # =================== GOVERNMENT/DBT PAYMENTS ===================
    {
        "sms": "Dear Customer, DBT/Govt. payment of Rs. 1,149.00 credited to your Acc No. XXXXX287151 on 15/12/25-SBI",
        "expected": {
            "type": "NET_BANKING",
            "category": "Government",
            "amount": 1149.00,
            "vendor": "DBT/Govt",
            "is_debit": False
        }
    },
    {
        "sms": "Dear Customer, DBT payment of Rs.500.00 credited to your Acc No. XXXXX123456 on 01/01/26. Scheme: PM KISAN -SBI",
        "expected": {
            "type": "NET_BANKING",
            "category": "Government",
            "amount": 500.00,
            "vendor": "PM KISAN",
            "is_debit": False
        }
    },
    {
        "sms": "DBT: Rs.2000 credited to your a/c XX7890 under LPG Subsidy. Ref: DBT123456789",
        "expected": {
            "type": "NET_BANKING",
            "category": "Government",
            "amount": 2000.00,
            "vendor": "LPG Subsidy",
            "is_debit": False
        }
    },
    
    # =================== ATM FEES/AMC CHARGES ===================
    {
        "sms": "Your AC XXXXX287151 Debited INR 201.97 on 17/11/25 -ATM PENDING AMC. Avl Bal INR 0.00.-SBI",
        "expected": {
            "type": "BANK_CHARGE",
            "category": "Bank Fees",
            "amount": 201.97,
            "vendor": "ATM AMC",
            "is_debit": True
        }
    },
    {
        "sms": "Your AC XXXXX287151 Debited INR 24.03 on 11/12/25 -ATM PENDING AMC. Avl Bal INR 176.97.-SBI",
        "expected": {
            "type": "BANK_CHARGE",
            "category": "Bank Fees",
            "amount": 24.03,
            "vendor": "ATM AMC",
            "is_debit": True
        }
    },
    {
        "sms": "HDFC: Rs.150 + GST debited from your a/c XX1234 towards Debit Card Annual Fee. Bal: Rs.5000",
        "expected": {
            "type": "BANK_CHARGE",
            "category": "Bank Fees",
            "amount": 150.00,
            "vendor": "Debit Card Annual Fee",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI: SMS Alert Charges of Rs.15 debited from your a/c XX5678 for Dec 2025",
        "expected": {
            "type": "BANK_CHARGE",
            "category": "Bank Fees",
            "amount": 15.00,
            "vendor": "SMS Alert Charges",
            "is_debit": True
        }
    },
    
    # =================== INTEREST CREDITS ===================
    {
        "sms": "An amount of INR 227.00 has been CREDITED to your account XXXXX06529 on 28/12/2025 towards interest. Total Avail.bal INR 33,647.18. - Canara Bank",
        "expected": {
            "type": "NET_BANKING",
            "category": "Interest",
            "amount": 227.00,
            "vendor": "Bank Interest",
            "is_debit": False
        }
    },
    {
        "sms": "SBI: Interest of Rs.456.78 credited to your a/c XX1234 for Q3 2025. New Bal: Rs.15,678.90",
        "expected": {
            "type": "NET_BANKING",
            "category": "Interest",
            "amount": 456.78,
            "vendor": "Bank Interest",
            "is_debit": False
        }
    },
    {
        "sms": "HDFC: Quarterly interest Rs.234.56 credited to your Savings a/c XX5678. Bal: Rs.12,345.67",
        "expected": {
            "type": "NET_BANKING",
            "category": "Interest",
            "amount": 234.56,
            "vendor": "Bank Interest",
            "is_debit": False
        }
    },
    
    # =================== CANARA BANK SMS (User Provided) ===================
    {
        "sms": "Your a/c no. XX6529 has been credited with Rs.1000.00 on 9/14/25 9:40 AM from a/c no. XX1381 (UPI Ref no 525723948467)-Canara Bank",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 1000.00,
            "vendor": "XX1381",
            "is_debit": False
        }
    },
    {
        "sms": "Your a/c no. XX6529 has been credited with Rs.1020.00 on 10/11/25 4:34 PM from a/c no. XX1381 (UPI Ref no 565029108314)-Canara Bank",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 1020.00,
            "vendor": "XX1381",
            "is_debit": False
        }
    },
    {
        "sms": "Your a/c no. XX6529 has been credited with Rs.510.00 on 10/11/25 6:08 PM from a/c no. XX2312 (UPI Ref no 528471341127)-Canara Bank",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 510.00,
            "vendor": "XX2312",
            "is_debit": False
        }
    },
    {
        "sms": "An amount of INR 72.00 has been DEBITED to your account XXXXX06529 on 16/12/2025. Total Avail.bal INR 36,329.08.Dial 1930 to report cyber fraud - Canara Bank",
        "expected": {
            "type": "OTHER",
            "category": "Other",
            "amount": 72.00,
            "vendor": "Unknown",
            "is_debit": True
        }
    },
    {
        "sms": "An amount of INR 350.90 has been DEBITED to your account XXXXX06529 on 19/12/2025. Total Avail.bal INR 35,978.18.Dial 1930 to report cyber fraud - Canara Bank",
        "expected": {
            "type": "OTHER",
            "category": "Other",
            "amount": 350.90,
            "vendor": "Unknown",
            "is_debit": True
        }
    },
    {
        "sms": "An amount of INR 1,318.00 has been DEBITED to your account XXXXX06529 on 23/12/2025. Total Avail.bal INR 34,560.18.Dial 1930 to report cyber fraud - Canara Bank",
        "expected": {
            "type": "OTHER",
            "category": "Other",
            "amount": 1318.00,
            "vendor": "Unknown",
            "is_debit": True
        }
    },
    
    # =================== RECHARGE/BILL PAYMENT CONFIRMATION ===================
    {
        "sms": "Hi, we have processed Rs. 349.0 for your Airtel Mobile 9594940316. The payment will be updated within 15 minutes. Please keep your order ID 7355891826785312768 for future reference.",
        "expected": {
            "type": "OTHER",
            "category": "Recharge",
            "amount": 349.00,
            "vendor": "Airtel Mobile",
            "is_debit": True
        }
    },
    {
        "sms": "Recharge of Rs.199 successful for Jio number 9876543210. Validity extended by 28 days.",
        "expected": {
            "type": "OTHER",
            "category": "Recharge",
            "amount": 199.00,
            "vendor": "Jio",
            "is_debit": True
        }
    },
    
    # =================== MORE UPI TRANSACTIONS (Various Banks) ===================
    {
        "sms": "HDFC Bank: Rs.250.00 sent to vegetable vendor via UPI. Ref:123456789012",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 250.00,
            "vendor": "vegetable vendor",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI: Rs.1200 paid to AUTO RIKSHA via UPI. Ref 234567890123. Bal Rs.8900",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 1200.00,
            "vendor": "AUTO RIKSHA",
            "is_debit": True
        }
    },
    {
        "sms": "Axis: UPI payment of Rs.599 to CHAI WALA successful. Ref:345678901234",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 599.00,
            "vendor": "CHAI WALA",
            "is_debit": True
        }
    },
    {
        "sms": "Kotak: Rs.89 debited via UPI to PARKING. Ref 456789012345. Bal Rs.12345",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 89.00,
            "vendor": "PARKING",
            "is_debit": True
        }
    },
    {
        "sms": "PNB: A/c XX1234 debited Rs.1500 via UPI to MEDICAL STORE. Ref:567890123456",
        "expected": {
            "type": "UPI",
            "category": "Healthcare",
            "amount": 1500.00,
            "vendor": "MEDICAL STORE",
            "is_debit": True
        }
    },
    {
        "sms": "BOB Alert: Rs.3000 paid via UPI to TAILOR SHOP. Ref:678901234567. Bal Rs.5678",
        "expected": {
            "type": "UPI",
            "category": "Services",
            "amount": 3000.00,
            "vendor": "TAILOR SHOP",
            "is_debit": True
        }
    },
    {
        "sms": "Union Bank: Rs.750 transferred via UPI to SALON. Ref:789012345678",
        "expected": {
            "type": "UPI",
            "category": "Services",
            "amount": 750.00,
            "vendor": "SALON",
            "is_debit": True
        }
    },
    {
        "sms": "IDBI: UPI debit of Rs.1800 to GYM TRAINER. Ref:890123456789. Bal Rs.4567",
        "expected": {
            "type": "UPI",
            "category": "Health & Fitness",
            "amount": 1800.00,
            "vendor": "GYM TRAINER",
            "is_debit": True
        }
    },
    {
        "sms": "Federal Bank: Rs.2500 sent to TUITION TEACHER via UPI. Ref:901234567890",
        "expected": {
            "type": "UPI",
            "category": "Education",
            "amount": 2500.00,
            "vendor": "TUITION TEACHER",
            "is_debit": True
        }
    },
    {
        "sms": "IndusInd: Rs.450 UPI payment to LOCAL GROCERY. Ref:012345678901. Bal Rs.6789",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 450.00,
            "vendor": "LOCAL GROCERY",
            "is_debit": True
        }
    },
    
    # =================== MORE CREDIT CARD TRANSACTIONS ===================
    {
        "sms": "HDFC CC XX1234 used for Rs.15,999 at ONEPLUS STORE on 28Dec25. Limit Avl: Rs.50,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 15999.00,
            "vendor": "ONEPLUS STORE",
            "is_debit": True
        }
    },
    {
        "sms": "SBI Card XX5678 charged Rs.2,499 at JIOMART on 27Dec25. Available limit: Rs.35,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 2499.00,
            "vendor": "JIOMART",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI CC ending 9012 used for Rs.899 at DECATHLON on 26Dec25. Call 18002662 if not you",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 899.00,
            "vendor": "DECATHLON",
            "is_debit": True
        }
    },
    {
        "sms": "Axis Credit Card XX3456 transaction Rs.5,499 at SAMSUNG STORE. Limit: Rs.40,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 5499.00,
            "vendor": "SAMSUNG STORE",
            "is_debit": True
        }
    },
    {
        "sms": "Kotak CC XX7890 used Rs.1,299 at LIFESTYLE on 25Dec25. Available limit Rs.28,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 1299.00,
            "vendor": "LIFESTYLE",
            "is_debit": True
        }
    },
    {
        "sms": "CITI Card ending 1111 charged Rs.3,999 at HAMLEYS on 24Dec25. Reply STOP to stop alerts",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 3999.00,
            "vendor": "HAMLEYS",
            "is_debit": True
        }
    },
    {
        "sms": "RBL CC XX2222 transaction of Rs.699 at MCDONALDS on 23Dec25. Avl Limit Rs.22,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Food & Dining",
            "amount": 699.00,
            "vendor": "MCDONALDS",
            "is_debit": True
        }
    },
    {
        "sms": "YES Bank CC XX3333 used for Rs.1,899 at CULT.FIT on 22Dec25. Balance: Rs.18,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Health & Fitness",
            "amount": 1899.00,
            "vendor": "CULT.FIT",
            "is_debit": True
        }
    },
    
    # =================== MORE SUBSCRIPTION SMS ===================
    {
        "sms": "Disney+ Hotstar: Rs.1,499 annual subscription renewed. Valid till 28Dec26.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 1499.00,
            "vendor": "Disney+ Hotstar",
            "is_debit": True
        }
    },
    {
        "sms": "Amazon Prime Video: Rs.179/month subscription charged successfully.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 179.00,
            "vendor": "Amazon Prime Video",
            "is_debit": True
        }
    },
    {
        "sms": "ZEE5: Rs.499 quarterly subscription auto-renewed. Next billing: 28Mar26",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 499.00,
            "vendor": "ZEE5",
            "is_debit": True
        }
    },
    {
        "sms": "SonyLIV: Rs.299/month subscription renewed on 28Dec25. Enjoy premium content!",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 299.00,
            "vendor": "SonyLIV",
            "is_debit": True
        }
    },
    {
        "sms": "Gaana Plus: Rs.99/month subscription renewed. Listen ad-free!",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 99.00,
            "vendor": "Gaana Plus",
            "is_debit": True
        }
    },
    {
        "sms": "Times Prime: Rs.1,199 annual membership renewed. Enjoy exclusive benefits!",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Other",
            "amount": 1199.00,
            "vendor": "Times Prime",
            "is_debit": True
        }
    },
    {
        "sms": "Practo Plus: Rs.449/3 months subscription renewed. Consult doctors anytime!",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Healthcare",
            "amount": 449.00,
            "vendor": "Practo Plus",
            "is_debit": True
        }
    },
    {
        "sms": "Cult.fit Live: Rs.999/month subscription active. Start your workout!",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Health & Fitness",
            "amount": 999.00,
            "vendor": "Cult.fit Live",
            "is_debit": True
        }
    },
    
    # =================== MORE DEBIT CARD/ATM ===================
    {
        "sms": "ATM: Rs.10,000 withdrawn from your HDFC a/c XX1234 at HDFC ATM MUMBAI. Bal: Rs.25,000",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Cash Withdrawal",
            "amount": 10000.00,
            "vendor": "HDFC ATM MUMBAI",
            "is_debit": True
        }
    },
    {
        "sms": "SBI ATM: Rs.5,000 withdrawn from your a/c X7890 at SBI ATM PUNE. Bal Rs.15,000",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Cash Withdrawal",
            "amount": 5000.00,
            "vendor": "SBI ATM PUNE",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI DC XX5678 used for Rs.3,500 at BIG BAZAAR via POS. Bal: Rs.12,000",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Shopping",
            "amount": 3500.00,
            "vendor": "BIG BAZAAR",
            "is_debit": True
        }
    },
    {
        "sms": "Axis Debit Card XX9012 swiped for Rs.2,100 at SHOPPER'S STOP. Bal Rs.8,000",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Shopping",
            "amount": 2100.00,
            "vendor": "SHOPPER'S STOP",
            "is_debit": True
        }
    },
    {
        "sms": "Kotak DC XX3456 POS transaction Rs.1,750 at CENTRAL MALL. Avl Bal Rs.6,000",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Shopping",
            "amount": 1750.00,
            "vendor": "CENTRAL MALL",
            "is_debit": True
        }
    },
    
    # =================== MORE NET BANKING ===================
    {
        "sms": "NEFT: Rs.25,000 transferred from your HDFC a/c to RENT ACCOUNT. Ref:HDFC123456789",
        "expected": {
            "type": "NET_BANKING",
            "category": "Rent",
            "amount": 25000.00,
            "vendor": "RENT ACCOUNT",
            "is_debit": True
        }
    },
    {
        "sms": "IMPS: Rs.10,000 sent from SBI a/c XX1234 to FREELANCER. Ref:SBI987654321",
        "expected": {
            "type": "NET_BANKING",
            "category": "Transfer",
            "amount": 10000.00,
            "vendor": "FREELANCER",
            "is_debit": True
        }
    },
    {
        "sms": "RTGS: Rs.1,00,000 credited to your ICICI a/c from COMPANY SALARY. Ref:ICICI456789",
        "expected": {
            "type": "NET_BANKING",
            "category": "Income",
            "amount": 100000.00,
            "vendor": "COMPANY SALARY",
            "is_debit": False
        }
    },
    {
        "sms": "Fund transfer of Rs.50,000 from your Axis a/c to INVESTMENT ACCOUNT via NEFT",
        "expected": {
            "type": "NET_BANKING",
            "category": "Investment",
            "amount": 50000.00,
            "vendor": "INVESTMENT ACCOUNT",
            "is_debit": True
        }
    },
    
    # =================== ELECTRICITY/WATER BILLS ===================
    {
        "sms": "MSEDCL: Electricity bill of Rs.1,234 paid successfully for Consumer No 123456789012",
        "expected": {
            "type": "OTHER",
            "category": "Utilities",
            "amount": 1234.00,
            "vendor": "MSEDCL",
            "is_debit": True
        }
    },
    {
        "sms": "TATA Power: Bill payment of Rs.2,567 received. Thank you for paying on time.",
        "expected": {
            "type": "OTHER",
            "category": "Utilities",
            "amount": 2567.00,
            "vendor": "TATA Power",
            "is_debit": True
        }
    },
    {
        "sms": "BSES: Rs.890 received towards electricity bill for K No 12345678. Thank you!",
        "expected": {
            "type": "OTHER",
            "category": "Utilities",
            "amount": 890.00,
            "vendor": "BSES",
            "is_debit": True
        }
    },
    {
        "sms": "Mumbai Municipal Water: Rs.450 paid for water bill. Consumer: WTR123456",
        "expected": {
            "type": "OTHER",
            "category": "Utilities",
            "amount": 450.00,
            "vendor": "Mumbai Municipal Water",
            "is_debit": True
        }
    },
    {
        "sms": "Mahanagar Gas: Bill of Rs.789 paid successfully for Customer ID MGL123456",
        "expected": {
            "type": "OTHER",
            "category": "Utilities",
            "amount": 789.00,
            "vendor": "Mahanagar Gas",
            "is_debit": True
        }
    },
    
    # =================== EDUCATION/SCHOOL FEES ===================
    {
        "sms": "Fee payment of Rs.15,000 received for Student ID STU123456. Thank you - ABC School",
        "expected": {
            "type": "OTHER",
            "category": "Education",
            "amount": 15000.00,
            "vendor": "ABC School",
            "is_debit": True
        }
    },
    {
        "sms": "College fees Rs.45,000 paid for Roll No 2024001. Receipt: CF2024123456",
        "expected": {
            "type": "OTHER",
            "category": "Education",
            "amount": 45000.00,
            "vendor": "College",
            "is_debit": True
        }
    },
    {
        "sms": "Exam fee of Rs.500 paid successfully for Enrollment: ENR123456. Good luck!",
        "expected": {
            "type": "OTHER",
            "category": "Education",
            "amount": 500.00,
            "vendor": "Exam Board",
            "is_debit": True
        }
    },
    
    # =================== INSURANCE PREMIUMS ===================
    {
        "sms": "HDFC Life: Premium of Rs.25,000 for Policy 12345678 debited. Next due: 28Dec26",
        "expected": {
            "type": "NET_BANKING",
            "category": "Insurance",
            "amount": 25000.00,
            "vendor": "HDFC Life",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI Prudential: Rs.12,500 insurance premium paid for Policy IP123456",
        "expected": {
            "type": "NET_BANKING",
            "category": "Insurance",
            "amount": 12500.00,
            "vendor": "ICICI Prudential",
            "is_debit": True
        }
    },
    {
        "sms": "Max Life Insurance: Premium Rs.8,000 received for Policy MAX123456. Thank you!",
        "expected": {
            "type": "NET_BANKING",
            "category": "Insurance",
            "amount": 8000.00,
            "vendor": "Max Life Insurance",
            "is_debit": True
        }
    },
    {
        "sms": "Star Health: Rs.15,000 health insurance premium paid. Policy: SH123456789",
        "expected": {
            "type": "NET_BANKING",
            "category": "Insurance",
            "amount": 15000.00,
            "vendor": "Star Health",
            "is_debit": True
        }
    },
    
    # =================== MUTUAL FUND SIP ===================
    {
        "sms": "SIP: Rs.5,000 invested in AXIS BLUECHIP FUND. Units: 45.67 NAV: 109.45",
        "expected": {
            "type": "NET_BANKING",
            "category": "Investment",
            "amount": 5000.00,
            "vendor": "AXIS BLUECHIP FUND",
            "is_debit": True
        }
    },
    {
        "sms": "SBI MF: SIP of Rs.3,000 processed for SBI SMALL CAP FUND. Units allotted: 25.34",
        "expected": {
            "type": "NET_BANKING",
            "category": "Investment",
            "amount": 3000.00,
            "vendor": "SBI SMALL CAP FUND",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI Pru MF: Rs.10,000 invested via SIP in ICICI PRU EQUITY FUND. NAV: 85.67",
        "expected": {
            "type": "NET_BANKING",
            "category": "Investment",
            "amount": 10000.00,
            "vendor": "ICICI PRU EQUITY FUND",
            "is_debit": True
        }
    },
    {
        "sms": "Nippon India MF: SIP Rs.2,500 for NIPPON INDIA LARGE CAP. Units: 18.90",
        "expected": {
            "type": "NET_BANKING",
            "category": "Investment",
            "amount": 2500.00,
            "vendor": "NIPPON INDIA LARGE CAP",
            "is_debit": True
        }
    },
    
    # =================== WALLET TOP-UPS ===================
    {
        "sms": "Paytm: Rs.2,000 added to your wallet. New Balance: Rs.2,500",
        "expected": {
            "type": "OTHER",
            "category": "Wallet Top-up",
            "amount": 2000.00,
            "vendor": "Paytm Wallet",
            "is_debit": True
        }
    },
    {
        "sms": "Amazon Pay: Rs.1,500 added to your wallet balance. Total: Rs.1,800",
        "expected": {
            "type": "OTHER",
            "category": "Wallet Top-up",
            "amount": 1500.00,
            "vendor": "Amazon Pay",
            "is_debit": True
        }
    },
    {
        "sms": "PhonePe: Rs.500 added to wallet. Balance: Rs.750. Enjoy cashless payments!",
        "expected": {
            "type": "OTHER",
            "category": "Wallet Top-up",
            "amount": 500.00,
            "vendor": "PhonePe Wallet",
            "is_debit": True
        }
    },
    
    # =================== PETROL/FUEL ===================
    {
        "sms": "Rs.2,000 paid at HP PETROL PUMP via UPI. Ref: 123456789012. Bal: Rs.5,000",
        "expected": {
            "type": "UPI",
            "category": "Fuel",
            "amount": 2000.00,
            "vendor": "HP PETROL PUMP",
            "is_debit": True
        }
    },
    {
        "sms": "IOCL: Rs.1,500 payment received at INDIAN OIL BHANDUP. Thank you!",
        "expected": {
            "type": "UPI",
            "category": "Fuel",
            "amount": 1500.00,
            "vendor": "INDIAN OIL BHANDUP",
            "is_debit": True
        }
    },
    {
        "sms": "BPCL: Rs.3,000 paid for fuel at BHARAT PETROLEUM ANDHERI. Ref: BP123456",
        "expected": {
            "type": "UPI",
            "category": "Fuel",
            "amount": 3000.00,
            "vendor": "BHARAT PETROLEUM ANDHERI",
            "is_debit": True
        }
    },
    
    # =================== MORE FOOD DELIVERY ===================
    {
        "sms": "Swiggy: Order #SW789012 of Rs.650 placed. Delivery by 8:45 PM",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 650.00,
            "vendor": "Swiggy",
            "is_debit": True
        }
    },
    {
        "sms": "Zomato: Rs.890 paid for order #ZMT456789. Arriving in 35 mins!",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 890.00,
            "vendor": "Zomato",
            "is_debit": True
        }
    },
    {
        "sms": "Dominos: Rs.599 order confirmed. Delivery in 30 minutes. Order ID: DOM123456",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 599.00,
            "vendor": "Dominos",
            "is_debit": True
        }
    },
    {
        "sms": "Pizza Hut: Rs.799 payment successful. Your order will arrive shortly!",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 799.00,
            "vendor": "Pizza Hut",
            "is_debit": True
        }
    },
    {
        "sms": "Box8: Order #BOX789 of Rs.450 confirmed. Delivery ETA 40 mins",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 450.00,
            "vendor": "Box8",
            "is_debit": True
        }
    },
    
    # =================== MORE E-COMMERCE ===================
    {
        "sms": "Amazon: Order #405-1234567 for Rs.4,999 shipped. Delivery by 30Dec25",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 4999.00,
            "vendor": "Amazon",
            "is_debit": True
        }
    },
    {
        "sms": "Flipkart: Rs.2,499 order #OD456789 confirmed. Expected delivery: 29Dec25",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 2499.00,
            "vendor": "Flipkart",
            "is_debit": True
        }
    },
    {
        "sms": "Myntra: Order #MYN123456 of Rs.1,899 placed. Track at myntra.com/orders",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 1899.00,
            "vendor": "Myntra",
            "is_debit": True
        }
    },
    {
        "sms": "Ajio: Rs.999 paid for Order #AJO789012. Delivery in 3-5 days",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 999.00,
            "vendor": "Ajio",
            "is_debit": True
        }
    },
    {
        "sms": "Meesho: Order #MSO456 of Rs.599 confirmed. Will be delivered by 01Jan26",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 599.00,
            "vendor": "Meesho",
            "is_debit": True
        }
    },
    {
        "sms": "Nykaa: Rs.1,299 order placed. Order ID: NYK789012. Delivery ETA 28Dec25",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 1299.00,
            "vendor": "Nykaa",
            "is_debit": True
        }
    },
    
    # =================== TICKET BOOKINGS ===================
    {
        "sms": "BookMyShow: Rs.1,200 paid for 2 tickets to PUSHPA 2 at INOX PHOENIX. Show: 8:30PM 28Dec",
        "expected": {
            "type": "OTHER",
            "category": "Entertainment",
            "amount": 1200.00,
            "vendor": "BookMyShow INOX",
            "is_debit": True
        }
    },
    {
        "sms": "PVR: Rs.900 booking confirmed for BAHUBALI 3 at PVR JUHU. 2 tickets for 7PM show",
        "expected": {
            "type": "OTHER",
            "category": "Entertainment",
            "amount": 900.00,
            "vendor": "PVR JUHU",
            "is_debit": True
        }
    },
    {
        "sms": "IRCTC: E-ticket for PNR 4567890123 booked. MUMBAI-DELHI 02Jan26. Fare: Rs.2,500",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 2500.00,
            "vendor": "IRCTC",
            "is_debit": True
        }
    },
    {
        "sms": "MakeMyTrip: Flight booking confirmed. DEL-BOM 05Jan26. Total: Rs.6,500",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 6500.00,
            "vendor": "MakeMyTrip",
            "is_debit": True
        }
    },
    {
        "sms": "Ixigo: Bus ticket booked. MUMBAI-PUNE 28Dec25. Rs.450. PNR: IX123456",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 450.00,
            "vendor": "Ixigo Bus",
            "is_debit": True
        }
    },
    {
        "sms": "RedBus: Rs.599 paid for MUMBAI-GOA bus on 01Jan26. Booking ID: RB789012",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 599.00,
            "vendor": "RedBus",
            "is_debit": True
        }
    },
    
    # =================== CAB/METRO ===================
    {
        "sms": "Uber: Rs.350 charged for trip to AIRPORT. Receipt at uber.com/receipts",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 350.00,
            "vendor": "Uber",
            "is_debit": True
        }
    },
    {
        "sms": "Ola: Rs.250 paid for ride from ANDHERI to BANDRA. Trip ID: OLA123456",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 250.00,
            "vendor": "Ola",
            "is_debit": True
        }
    },
    {
        "sms": "Rapido: Rs.89 bike ride completed. Thanks for riding with us!",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 89.00,
            "vendor": "Rapido",
            "is_debit": True
        }
    },
    {
        "sms": "Delhi Metro: Rs.60 deducted from your card for RAJIV CHOWK to HAUZ KHAS",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 60.00,
            "vendor": "Delhi Metro",
            "is_debit": True
        }
    },
    {
        "sms": "Mumbai Metro: Rs.40 fare charged from ANDHERI to GHATKOPAR. Card bal: Rs.150",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 40.00,
            "vendor": "Mumbai Metro",
            "is_debit": True
        }
    },
    
    # =================== GROCERY APPS ===================
    {
        "sms": "BigBasket: Order #BB123456 of Rs.1,850 confirmed. Delivery: Tomorrow 10AM-12PM",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 1850.00,
            "vendor": "BigBasket",
            "is_debit": True
        }
    },
    {
        "sms": "Blinkit: Rs.450 order placed. Delivery in 10 minutes! Order ID: BL789",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 450.00,
            "vendor": "Blinkit",
            "is_debit": True
        }
    },
    {
        "sms": "Zepto: Order #ZEP456 of Rs.320 confirmed. Arriving in 8 mins!",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 320.00,
            "vendor": "Zepto",
            "is_debit": True
        }
    },
    {
        "sms": "Instamart: Rs.890 order placed. Delivery in 15 minutes. Order: IM12345",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 890.00,
            "vendor": "Swiggy Instamart",
            "is_debit": True
        }
    },
    {
        "sms": "JioMart: Order of Rs.1,200 confirmed. Delivery slot: Tomorrow 4PM-6PM",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 1200.00,
            "vendor": "JioMart",
            "is_debit": True
        }
    },
    
    # =================== MORE NO_TRANSACTION: PROMOTIONAL ===================
    {
        "sms": "HDFC Bank: Get 5% cashback on your Credit Card! Offer valid till 31Dec. T&C apply.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "HDFC Bank",
            "is_debit": False
        }
    },
    {
        "sms": "Flipkart Year End Sale! Flat 50% off on Electronics. Shop now!",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Flipkart",
            "is_debit": False
        }
    },
    {
        "sms": "Amazon Great Indian Sale starts tomorrow! Get ready for amazing deals.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "Amazon",
            "is_debit": False
        }
    },
    {
        "sms": "JIO: Upgrade to 5G plan for Rs.239/month. Enjoy blazing fast internet!",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "JIO",
            "is_debit": False
        }
    },
    {
        "sms": "ICICI Bank: Pre-approved personal loan up to Rs.10 lakh! Apply now.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Promotional",
            "amount": 0.00,
            "vendor": "ICICI Bank",
            "is_debit": False
        }
    },
    
    # =================== MORE UPI TRANSACTIONS ===================
    {
        "sms": "SBI: Rs.1500 paid to DOCTOR via UPI. Ref: 123456789. Bal: Rs.8000",
        "expected": {
            "type": "UPI",
            "category": "Healthcare",
            "amount": 1500.00,
            "vendor": "DOCTOR",
            "is_debit": True
        }
    },
    {
        "sms": "HDFC: Rs.300 sent to NEWSPAPER VENDOR via UPI. Ref: 987654321",
        "expected": {
            "type": "UPI",
            "category": "Services",
            "amount": 300.00,
            "vendor": "NEWSPAPER VENDOR",
            "is_debit": True
        }
    },
    {
        "sms": "Axis: UPI payment Rs.5000 to PLUMBER successful. Ref: 456789123",
        "expected": {
            "type": "UPI",
            "category": "Services",
            "amount": 5000.00,
            "vendor": "PLUMBER",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI: Rs.250 paid to LAUNDRY via UPI. Ref: 789123456. Bal Rs.6000",
        "expected": {
            "type": "UPI",
            "category": "Services",
            "amount": 250.00,
            "vendor": "LAUNDRY",
            "is_debit": True
        }
    },
    {
        "sms": "Kotak: Rs.850 UPI transfer to MAID. Ref: 321654987. Bal Rs.12000",
        "expected": {
            "type": "UPI",
            "category": "Services",
            "amount": 850.00,
            "vendor": "MAID",
            "is_debit": True
        }
    },
    
    # =================== MORE CREDIT CARDS ===================
    {
        "sms": "HDFC CC XX1234 used Rs.45,000 at APPLE STORE. Limit: Rs.120,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 45000.00,
            "vendor": "APPLE STORE",
            "is_debit": True
        }
    },
    {
        "sms": "SBI Card XX5678 charged Rs.8,999 at LG ELECTRONICS. Avl Limit: Rs.75,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Shopping",
            "amount": 8999.00,
            "vendor": "LG ELECTRONICS",
            "is_debit": True
        }
    },
    {
        "sms": "Axis CC XX9012 transaction Rs.2,500 at PHARMEASY. Limit: Rs.40,000",
        "expected": {
            "type": "CREDIT_CARD",
            "category": "Healthcare",
            "amount": 2500.00,
            "vendor": "PHARMEASY",
            "is_debit": True
        }
    },
    
    # =================== MORE SUBSCRIPTIONS ===================
    {
        "sms": "Netflix: Rs.649 monthly subscription charged. Valid till 28Jan26.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 649.00,
            "vendor": "Netflix",
            "is_debit": True
        }
    },
    {
        "sms": "Spotify: Rs.119/month auto-renewed. Enjoy ad-free music!",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Entertainment",
            "amount": 119.00,
            "vendor": "Spotify",
            "is_debit": True
        }
    },
    {
        "sms": "iCloud: Rs.75/month storage plan renewed. 50GB storage active.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Cloud Storage",
            "amount": 75.00,
            "vendor": "iCloud",
            "is_debit": True
        }
    },
    {
        "sms": "Google One: Rs.130/month subscription renewed. 100GB storage active.",
        "expected": {
            "type": "SUBSCRIPTION",
            "category": "Cloud Storage",
            "amount": 130.00,
            "vendor": "Google One",
            "is_debit": True
        }
    },
    
    # =================== OTP AND AUTH MESSAGES ===================
    {
        "sms": "Your OTP for SBI transaction is 456789. Valid for 3 minutes. Do not share.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "OTP",
            "amount": 0.00,
            "vendor": "SBI",
            "is_debit": False
        }
    },
    {
        "sms": "HDFC: Your One Time Password for online transaction is 123456. Valid for 5 mins.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "OTP",
            "amount": 0.00,
            "vendor": "HDFC",
            "is_debit": False
        }
    },
    {
        "sms": "Amazon OTP: 789012. Use this to verify your login. Don't share with anyone.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "OTP",
            "amount": 0.00,
            "vendor": "Amazon",
            "is_debit": False
        }
    },
    
    # =================== BALANCE ENQUIRY ===================
    {
        "sms": "SBI: Your account X7151 balance as on 28Dec25 is Rs.15,678.90. Thank you for banking with SBI.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Balance Enquiry",
            "amount": 15678.90,
            "vendor": "SBI",
            "is_debit": False
        }
    },
    {
        "sms": "HDFC: Available balance in a/c XX1234 is Rs.25,432.50 as on 28Dec25 10:30 AM.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Balance Enquiry",
            "amount": 25432.50,
            "vendor": "HDFC",
            "is_debit": False
        }
    },
    
    # =================== LOAN DISBURSEMENT ===================
    {
        "sms": "HDFC: Personal Loan of Rs.5,00,000 disbursed to your a/c XX1234. EMI starts from 05Feb26.",
        "expected": {
            "type": "NET_BANKING",
            "category": "Loan",
            "amount": 500000.00,
            "vendor": "HDFC Personal Loan",
            "is_debit": False
        }
    },
    {
        "sms": "Bajaj Finance: Rs.1,50,000 loan amount credited to your bank a/c. EMI: Rs.5,500/month.",
        "expected": {
            "type": "NET_BANKING",
            "category": "Loan",
            "amount": 150000.00,
            "vendor": "Bajaj Finance",
            "is_debit": False
        }
    },
    
    # =================== CREDIT CARD BILL PAYMENT ===================
    {
        "sms": "Thank you! Rs.15,000 received towards your HDFC CC XX5678. Outstanding: Rs.0",
        "expected": {
            "type": "OTHER",
            "category": "Credit Card Payment",
            "amount": 15000.00,
            "vendor": "HDFC Credit Card",
            "is_debit": True
        }
    },
    {
        "sms": "ICICI CC XX9012: Payment of Rs.8,500 received. Thanks for paying on time!",
        "expected": {
            "type": "OTHER",
            "category": "Credit Card Payment",
            "amount": 8500.00,
            "vendor": "ICICI Credit Card",
            "is_debit": True
        }
    },
    
    # =================== MORE DEBIT CARD ===================
    {
        "sms": "POS: Rs.4,500 debited from your HDFC DC XX1234 at CROSSWORD BOOKS. Bal: Rs.18,000",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Shopping",
            "amount": 4500.00,
            "vendor": "CROSSWORD BOOKS",
            "is_debit": True
        }
    },
    {
        "sms": "SBI DC XX5678 used for Rs.1,800 at INOX CINEMAS via POS. Bal Rs.9,500",
        "expected": {
            "type": "DEBIT_CARD",
            "category": "Entertainment",
            "amount": 1800.00,
            "vendor": "INOX CINEMAS",
            "is_debit": True
        }
    },
    
    # =================== RENT PAYMENTS ===================
    {
        "sms": "NEFT: Rs.18,000 transferred to LANDLORD PROPERTY for rent. Ref: RENT202512",
        "expected": {
            "type": "NET_BANKING",
            "category": "Rent",
            "amount": 18000.00,
            "vendor": "LANDLORD PROPERTY",
            "is_debit": True
        }
    },
    {
        "sms": "UPI: Rs.22,000 paid to APARTMENT RENT via UPI. Ref: 123456789012",
        "expected": {
            "type": "UPI",
            "category": "Rent",
            "amount": 22000.00,
            "vendor": "APARTMENT RENT",
            "is_debit": True
        }
    },
    
    # =================== FASTAG ===================
    {
        "sms": "FASTag: Rs.85 toll charged at MUMBAI EXPRESSWAY. Bal: Rs.245. Recharge on Paytm.",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 85.00,
            "vendor": "FASTag MUMBAI EXPRESSWAY",
            "is_debit": True
        }
    },
    {
        "sms": "IHMCL: FASTag Rs.120 deducted at PUNE-BANGALORE TOLL. Balance: Rs.380",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 120.00,
            "vendor": "FASTag PUNE-BANGALORE",
            "is_debit": True
        }
    },
    
    # =================== DONATION ===================
    {
        "sms": "Thank you for donating Rs.1,000 to PM CARES FUND. Receipt ID: PMC123456789",
        "expected": {
            "type": "OTHER",
            "category": "Donation",
            "amount": 1000.00,
            "vendor": "PM CARES FUND",
            "is_debit": True
        }
    },
    {
        "sms": "CRY India: Rs.500 donation received. Thank you for supporting child rights!",
        "expected": {
            "type": "OTHER",
            "category": "Donation",
            "amount": 500.00,
            "vendor": "CRY India",
            "is_debit": True
        }
    },
    
    # =================== BONUS/REWARDS CREDIT ===================
    {
        "sms": "Congratulations! Rs.250 cashback credited to your Paytm wallet for Diwali offer.",
        "expected": {
            "type": "OTHER",
            "category": "Cashback",
            "amount": 250.00,
            "vendor": "Paytm Cashback",
            "is_debit": False
        }
    },
    {
        "sms": "Amazon: Rs.100 cashback credited for your recent purchase. Check Amazon Pay.",
        "expected": {
            "type": "OTHER",
            "category": "Cashback",
            "amount": 100.00,
            "vendor": "Amazon Cashback",
            "is_debit": False
        }
    },
    
    # ===================================================================================
    # LLM-ONLY COMPLEX SMS SAMPLES (33 samples)
    # These require contextual understanding, cannot be parsed by simple regex
    # Flag: require_llm = True
    # ===================================================================================
    
    # --- Contextual Reasoning Required ---
    {
        "sms": "bhai tune jo 500 diye the wo return kar diye hai check kar",
        "expected": {
            "type": "UPI",
            "category": "Transfer",
            "amount": 500.00,
            "vendor": "Friend",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Casual Hindi with implicit payment context"
    },
    {
        "sms": "kal ka dinner ka paisa bhej diya 1200 rs upi se",
        "expected": {
            "type": "UPI",
            "category": "Food & Dining",
            "amount": 1200.00,
            "vendor": "Friend",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Casual Hindi, implicit payment"
    },
    {
        "sms": "ur acct xxx7890 paid to merchant amnt of fifteen hundred only",
        "expected": {
            "type": "UPI",
            "category": "Other",
            "amount": 1500.00,
            "vendor": "merchant",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Amount in words not digits"
    },
    {
        "sms": "You sent two thousand five hundred rupees to grocery shop via gpay",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 2500.00,
            "vendor": "grocery shop",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Amount in words"
    },
    {
        "sms": "Got ur transfer of 3k for the laptop. Thanks!",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 3000.00,
            "vendor": "Unknown",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Shorthand '3k' requires interpretation"
    },
    {
        "sms": "Sent 5k to mom for groceries",
        "expected": {
            "type": "UPI",
            "category": "Transfer",
            "amount": 5000.00,
            "vendor": "mom",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Shorthand '5k', no bank format"
    },
    {
        "sms": "paid 2.5k for uber today morning ride to airport",
        "expected": {
            "type": "UPI",
            "category": "Transportation",
            "amount": 2500.00,
            "vendor": "uber",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Shorthand '2.5k' requires parsing"
    },
    
    # --- Abbreviated/Incomplete Bank SMS ---
    {
        "sms": "Dbtd 999 ref 1234 bal 5432",
        "expected": {
            "type": "OTHER",
            "category": "Other",
            "amount": 999.00,
            "vendor": "Unknown",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Heavily abbreviated SMS"
    },
    {
        "sms": "ac xx567 cr 10k NEFT frm salary",
        "expected": {
            "type": "NET_BANKING",
            "category": "Income",
            "amount": 10000.00,
            "vendor": "salary",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Heavily abbreviated with '10k'"
    },
    {
        "sms": "txn 5678 amt 2lak db for car advance payment",
        "expected": {
            "type": "NET_BANKING",
            "category": "Vehicle",
            "amount": 200000.00,
            "vendor": "Car Dealer",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "'2lak' requires understanding Indian numbering"
    },
    
    # --- Mixed/Jumbled Format ---
    {
        "sms": "payment 1,50,000 done for property registration at SRO mumbai cheque no 456789",
        "expected": {
            "type": "NET_BANKING",
            "category": "Government",
            "amount": 150000.00,
            "vendor": "SRO mumbai",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Non-standard format, needs context for category"
    },
    {
        "sms": "Booked flight DEL-BOM for next week payment of 6799 completed confirmation will follow",
        "expected": {
            "type": "OTHER",
            "category": "Transportation",
            "amount": 6799.00,
            "vendor": "Flight Booking",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Conversational style, embedded amount"
    },
    {
        "sms": "The medicine bill came to around 2345 rupees paid at apollo pharmacy thankyou for visiting",
        "expected": {
            "type": "OTHER",
            "category": "Healthcare",
            "amount": 2345.00,
            "vendor": "apollo pharmacy",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Conversational format"
    },
    
    # --- Contextual Category Inference ---
    {
        "sms": "Paid tuition fees for Sharma Coaching Classes amount 8500",
        "expected": {
            "type": "OTHER",
            "category": "Education",
            "amount": 8500.00,
            "vendor": "Sharma Coaching Classes",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Category inference from context"
    },
    {
        "sms": "gym membership renewed for 3 months total 4500 at Gold's Gym Andheri",
        "expected": {
            "type": "OTHER",
            "category": "Health & Fitness",
            "amount": 4500.00,
            "vendor": "Gold's Gym Andheri",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Needs context to categorize"
    },
    {
        "sms": "annual society maintenance of 12000 paid via NEFT to XYZ Housing",
        "expected": {
            "type": "NET_BANKING",
            "category": "Housing",
            "amount": 12000.00,
            "vendor": "XYZ Housing",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Category inference"
    },
    {
        "sms": "Donated 2500 to local temple trust for navratri celebrations",
        "expected": {
            "type": "OTHER",
            "category": "Donation",
            "amount": 2500.00,
            "vendor": "temple trust",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Category inference from context"
    },
    
    # --- Ambiguous Transaction Direction ---
    {
        "sms": "Settlement of 25000 processed between you and John regarding the old laptop deal",
        "expected": {
            "type": "OTHER",
            "category": "Transfer",
            "amount": 25000.00,
            "vendor": "John",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Ambiguous direction, needs reasoning"
    },
    {
        "sms": "Adjustment of 5000 made for the extra payment last month",
        "expected": {
            "type": "OTHER",
            "category": "Adjustment",
            "amount": 5000.00,
            "vendor": "Unknown",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Needs context to determine debit/credit"
    },
    
    # --- Complex Multi-Transaction Messages ---
    {
        "sms": "Monthly summary: spent 15000 on food, 8000 on transport, 3000 on entertainment total 26000 this month",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Summary",
            "amount": 26000.00,
            "vendor": "Monthly Summary",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Summary message, not actual transaction"
    },
    {
        "sms": "Bill split: Your share is 876 out of total 4380 for dinner at Mainland China paid by Rahul",
        "expected": {
            "type": "OTHER",
            "category": "Food & Dining",
            "amount": 876.00,
            "vendor": "Mainland China",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Bill split logic, extracting correct amount"
    },
    {
        "sms": "Group expense: Rahul paid 3000, you owe him 1000 for the movie tickets",
        "expected": {
            "type": "OTHER",
            "category": "Entertainment",
            "amount": 1000.00,
            "vendor": "Rahul",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Group expense logic"
    },
    
    # --- Negative/Reversal Transactions ---
    {
        "sms": "Your dispute for 2999 at Fraudulent Merchant has been resolved. Amount reversed to your account.",
        "expected": {
            "type": "OTHER",
            "category": "Refund",
            "amount": 2999.00,
            "vendor": "Dispute Resolution",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Dispute resolution context"
    },
    {
        "sms": "Chargeback initiated for unauthorized transaction of 15000 at Unknown Store. Investigation ongoing.",
        "expected": {
            "type": "NO_TRANSACTION",
            "category": "Chargeback",
            "amount": 15000.00,
            "vendor": "Unknown Store",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Chargeback is pending, not completed"
    },
    
    # --- Implied Amounts ---
    {
        "sms": "Your fixed deposit of principal amount five lakh matured. Interest of 45000 credited.",
        "expected": {
            "type": "NET_BANKING",
            "category": "Interest",
            "amount": 45000.00,
            "vendor": "FD Interest",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Need to identify which amount is credited"
    },
    {
        "sms": "Loan EMI of 12500 debited. Outstanding principal 180000. Interest component 2890.",
        "expected": {
            "type": "NET_BANKING",
            "category": "EMI",
            "amount": 12500.00,
            "vendor": "Loan EMI",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Multiple amounts, need to identify EMI"
    },
    
    # --- Regional Language Mixed ---
    {
        "sms": "Tumhara payment hogaya 2500 ka jo tune Shopkeeper ko diya tha UPI se",
        "expected": {
            "type": "UPI",
            "category": "Shopping",
            "amount": 2500.00,
            "vendor": "Shopkeeper",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Hindi conversational"
    },
    {
        "sms": "Paisa aagaya bhai 10000 wala jo tune bheja tha party ke liye",
        "expected": {
            "type": "UPI",
            "category": "Income",
            "amount": 10000.00,
            "vendor": "Friend",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Colloquial Hindi"
    },
    {
        "sms": "rent ka paisa de diya landlord ko 18000 UPI kar diya aaj",
        "expected": {
            "type": "UPI",
            "category": "Rent",
            "amount": 18000.00,
            "vendor": "landlord",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Colloquial Hindi with context"
    },
    
    # --- Sarcastic/Unusual Phrasing ---
    {
        "sms": "There goes another 5000 from my account. Thanks for nothing, impulse buying!",
        "expected": {
            "type": "OTHER",
            "category": "Shopping",
            "amount": 5000.00,
            "vendor": "Unknown",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Sarcastic tone, needs sentiment understanding"
    },
    {
        "sms": "Finally got back the 3000 that was stuck in that cancelled order for ages!",
        "expected": {
            "type": "OTHER",
            "category": "Refund",
            "amount": 3000.00,
            "vendor": "Refund",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Conversational, implies refund"
    },
    
    # --- Technical/Crypto ---
    {
        "sms": "Bought 0.003 ETH worth about 2500 INR on WazirX. Keep hodling!",
        "expected": {
            "type": "OTHER",
            "category": "Investment",
            "amount": 2500.00,
            "vendor": "WazirX",
            "is_debit": True
        },
        "require_llm": True,
        "reason": "Crypto context, INR extraction"
    },
    {
        "sms": "Sold some BTC profit of around 15k moved to bank. Good trade!",
        "expected": {
            "type": "OTHER",
            "category": "Investment",
            "amount": 15000.00,
            "vendor": "Crypto Trade",
            "is_debit": False
        },
        "require_llm": True,
        "reason": "Crypto sale, '15k' shorthand"
    },
]

# Summary statistics - will be computed dynamically
DATASET_STATS = {
    "total_samples": len(TEST_SMS_DATASET),
    "by_type": {},
    "by_category": {}
}

# Compute stats dynamically
for sample in TEST_SMS_DATASET:
    t = sample["expected"]["type"]
    c = sample["expected"]["category"]
    DATASET_STATS["by_type"][t] = DATASET_STATS["by_type"].get(t, 0) + 1
    DATASET_STATS["by_category"][c] = DATASET_STATS["by_category"].get(c, 0) + 1

if __name__ == "__main__":
    print(f"Total SMS samples: {len(TEST_SMS_DATASET)}")
    print("\nSamples by type:")
    for sms_type, count in sorted(DATASET_STATS["by_type"].items(), key=lambda x: -x[1]):
        print(f"  {sms_type}: {count}")
    print("\nSamples by category:")
    for category, count in sorted(DATASET_STATS["by_category"].items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")

