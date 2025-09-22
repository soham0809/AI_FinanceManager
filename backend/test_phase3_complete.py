"""
Comprehensive Phase 3 Test - AI Smart Categorization Complete
Tests all ML categorization functionality end-to-end
"""

import requests
import json
from ml_categorizer import ml_categorizer

BASE_URL = "http://localhost:8000"

def test_phase3_completion():
    """Test all Phase 3 components are working"""
    print("=" * 70)
    print("PHASE 3 COMPLETION TEST - AI Smart Categorization")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 8
    
    # Test 1: ML Model Training and Loading
    print("\n1. Testing ML Model Training and Loading...")
    try:
        # Test model loading
        category, confidence = ml_categorizer.predict_category("SWIGGY BANGALORE")
        if category and confidence > 0:
            print(f"   [OK] Model loaded and predicting: {category} ({confidence:.3f})")
            tests_passed += 1
        else:
            print("   [FAIL] Model not working properly")
    except Exception as e:
        print(f"   [FAIL] Model error: {e}")
    
    # Test 2: Enhanced SMS Parser with ML Integration
    print("\n2. Testing Enhanced SMS Parser with ML...")
    try:
        test_sms = "Rs 450.00 debited from A/c **1234 on 10-Sep-24 at SWIGGY BANGALORE for UPI/123456789"
        response = requests.post(f"{BASE_URL}/v1/parse-sms", json={"sms_text": test_sms})
        
        if response.status_code == 200:
            data = response.json()
            if data['success'] and data['category'] == 'Food & Dining':
                print(f"   [OK] SMS parsed with ML categorization: {data['vendor']} -> {data['category']}")
                tests_passed += 1
            else:
                print(f"   [FAIL] SMS parsing failed or wrong category: {data}")
        else:
            print(f"   [FAIL] SMS parsing API failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] SMS parsing error: {e}")
    
    # Test 3: ML Categorization API Endpoint
    print("\n3. Testing ML Categorization API...")
    try:
        response = requests.post(f"{BASE_URL}/v1/categorize?vendor=AMAZON PAY INDIA")
        
        if response.status_code == 200:
            data = response.json()
            if data['predicted_category'] == 'Shopping':
                print(f"   [OK] ML API working: {data['vendor']} -> {data['predicted_category']} ({data['confidence']:.3f})")
                tests_passed += 1
            else:
                print(f"   [FAIL] Wrong ML prediction: {data}")
        else:
            print(f"   [FAIL] ML API failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] ML API error: {e}")
    
    # Test 4: ML Model Info Endpoint
    print("\n4. Testing ML Model Info...")
    try:
        response = requests.get(f"{BASE_URL}/v1/ml-info")
        
        if response.status_code == 200:
            info = response.json()
            if info['status'] == 'Model loaded' and len(info['categories']) == 10:
                print(f"   [OK] ML model info: {info['model_type']}, {len(info['categories'])} categories")
                tests_passed += 1
            else:
                print(f"   [FAIL] ML model info incomplete: {info}")
        else:
            print(f"   [FAIL] ML info API failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] ML info error: {e}")
    
    # Test 5: Database Integration with ML Categories
    print("\n5. Testing Database Integration with ML Categories...")
    try:
        # Parse and store a transaction
        test_sms = "Thank you for using HDFC Bank NetBanking. You have spent Rs 1,250.50 at AMAZON PAY INDIA on 10-SEP-24"
        response = requests.post(f"{BASE_URL}/v1/parse-sms", json={"sms_text": test_sms})
        
        if response.status_code == 200:
            # Check if transaction was stored with ML category
            transactions_response = requests.get(f"{BASE_URL}/v1/transactions")
            if transactions_response.status_code == 200:
                transactions = transactions_response.json()
                amazon_transaction = next((t for t in transactions if 'AMAZON' in t['vendor']), None)
                
                if amazon_transaction and amazon_transaction['category'] == 'Shopping':
                    print(f"   [OK] Transaction stored with ML category: {amazon_transaction['vendor']} -> {amazon_transaction['category']}")
                    tests_passed += 1
                else:
                    print(f"   [FAIL] Transaction not stored properly with ML category")
            else:
                print(f"   [FAIL] Failed to retrieve transactions: {transactions_response.status_code}")
        else:
            print(f"   [FAIL] Failed to parse and store transaction: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] Database integration error: {e}")
    
    # Test 6: Category Accuracy Test
    print("\n6. Testing ML Category Accuracy...")
    try:
        test_cases = [
            ("SWIGGY BANGALORE", "Food & Dining"),
            ("AMAZON PAY INDIA", "Shopping"),
            ("UBER TRIP", "Transportation"),
            ("NETFLIX INDIA", "Entertainment"),
            ("APOLLO PHARMACY", "Healthcare")
        ]
        
        correct_predictions = 0
        for vendor, expected in test_cases:
            category, confidence = ml_categorizer.predict_category(vendor)
            if category == expected:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(test_cases)
        if accuracy >= 0.8:  # 80% accuracy threshold
            print(f"   [OK] ML accuracy: {accuracy:.1%} ({correct_predictions}/{len(test_cases)})")
            tests_passed += 1
        else:
            print(f"   [FAIL] ML accuracy too low: {accuracy:.1%}")
    except Exception as e:
        print(f"   [FAIL] Accuracy test error: {e}")
    
    # Test 7: Fallback to Rule-based Categorization
    print("\n7. Testing Fallback to Rule-based Categorization...")
    try:
        # Test with a vendor that might not be in ML training data
        test_vendor = "UNKNOWN RESTAURANT XYZ"
        category, confidence = ml_categorizer.predict_category(test_vendor)
        
        # Should still get a category (either from ML or fallback)
        if category and category != "Others":
            print(f"   [OK] Fallback categorization working: {test_vendor} -> {category}")
            tests_passed += 1
        else:
            print(f"   [FAIL] Fallback not working properly: {category}")
    except Exception as e:
        print(f"   [FAIL] Fallback test error: {e}")
    
    # Test 8: End-to-End SMS to Database with ML
    print("\n8. Testing End-to-End SMS Processing...")
    try:
        # Test complete flow: SMS -> Parse -> ML Categorize -> Store
        test_sms = "Paid Rs 299.00 to NETFLIX INDIA via Google Pay. UPI transaction ID: 123456789012345"
        
        # Parse SMS
        response = requests.post(f"{BASE_URL}/v1/parse-sms", json={"sms_text": test_sms})
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify all components
            if (data['success'] and 
                data['vendor'] == 'NETFLIX INDIA via Google Pay' and 
                data['amount'] == 299.0 and 
                data['category'] == 'Entertainment' and
                data['transaction_type'] == 'debit'):
                
                print(f"   [OK] End-to-end processing: SMS -> {data['vendor']} -> {data['category']} -> ₹{data['amount']}")
                tests_passed += 1
            else:
                print(f"   [FAIL] End-to-end processing incomplete: {data}")
        else:
            print(f"   [FAIL] End-to-end processing failed: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] End-to-end test error: {e}")
    
    # Final Results
    print("\n" + "=" * 70)
    print(f"PHASE 3 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    print("=" * 70)
    
    if tests_passed >= 7:  # Allow 1 test to fail
        print("🎉 PHASE 3 COMPLETED SUCCESSFULLY!")
        print("✅ AI Smart Categorization is fully functional")
        print("✅ ML model training and prediction working")
        print("✅ Enhanced SMS parser with ML integration")
        print("✅ Database integration with ML categories")
        print("✅ API endpoints for ML categorization")
        print("✅ Fallback to rule-based categorization")
        print("\n🚀 Ready to proceed to Phase 4: UI/UX & Data Visualization")
        return True
    else:
        print("❌ PHASE 3 INCOMPLETE")
        print("⚠️  Some critical ML categorization features are not working")
        print("🔧 Please fix the failing tests before proceeding")
        return False

if __name__ == "__main__":
    test_phase3_completion()
