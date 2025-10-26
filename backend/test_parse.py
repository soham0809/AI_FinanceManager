#!/usr/bin/env python3
"""Test parsing directly"""
import sys
sys.path.insert(0, '.')

try:
    from app.controllers.transaction_controller import TransactionController
    from app.config.database import SessionLocal
    
    print("✅ Imports successful")
    
    # Test local parsing
    controller = TransactionController()
    db = SessionLocal()
    
    sms_text = "Rs.250.00 debited from A/c XX1234 on 15-Oct-25 to Swiggy"
    
    print(f"\n📱 Testing SMS: {sms_text}")
    
    result = controller.parse_sms_local_quick(db, sms_text, user_id=None)
    
    if result.get('success'):
        transaction = result['transaction']
        print(f"\n✅ Parsing successful!")
        print(f"  Vendor: {transaction.vendor}")
        print(f"  Amount: {transaction.amount}")
        print(f"  Category: {transaction.category}")
        print(f"  Transaction Type: {transaction.transaction_type}")
        print(f"  Date: {transaction.date}")
    else:
        print(f"\n❌ Parsing failed: {result.get('error')}")
    
    db.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
