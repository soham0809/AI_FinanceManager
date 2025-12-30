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
]

# Summary statistics
DATASET_STATS = {
    "total_samples": len(TEST_SMS_DATASET),
    "by_type": {
        "UPI": 12,
        "CREDIT_CARD": 7,
        "DEBIT_CARD": 4,
        "SUBSCRIPTION": 10,
        "NET_BANKING": 4,
        "OTHER": 13
    },
    "by_category": {
        "Food & Dining": 8,
        "Shopping": 14,
        "Transportation": 7,
        "Entertainment": 5,
        "Healthcare": 3,
        "Education": 3,
        "Utilities": 5,
        "Income": 4,
        "Rent": 1
    }
}

if __name__ == "__main__":
    print(f"Total SMS samples: {len(TEST_SMS_DATASET)}")
    print("\nSamples by type:")
    for sms_type, count in DATASET_STATS["by_type"].items():
        print(f"  {sms_type}: {count}")
    print("\nSamples by category:")
    for category, count in DATASET_STATS["by_category"].items():
        print(f"  {category}: {count}")
