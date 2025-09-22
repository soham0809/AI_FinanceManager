"""
Test ML-powered categorization functionality
"""

import requests
from ml_categorizer import ml_categorizer

BASE_URL = "http://localhost:8000"

def test_ml_categorizer_direct():
    """Test ML categorizer directly"""
    print("Testing ML Categorizer directly...")
    
    test_vendors = [
        "SWIGGY BANGALORE",
        "AMAZON PAY INDIA", 
        "UBER TRIP",
        "NETFLIX INDIA",
        "APOLLO PHARMACY",
        "BYJUS CLASSES",
        "ELECTRICITY BILL PAYMENT",
        "HP PETROL PUMP"
    ]
    
    for vendor in test_vendors:
        category, confidence = ml_categorizer.predict_category(vendor)
        print(f"  {vendor:<25} -> {category:<15} (confidence: {confidence:.3f})")
    
    return True

def test_ml_api_endpoint():
    """Test ML categorization API endpoint"""
    print("\nTesting ML categorization API...")
    
    test_vendor = "SWIGGY BANGALORE"
    
    response = requests.post(
        f"{BASE_URL}/v1/categorize",
        params={"vendor": test_vendor}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] API categorization successful:")
        print(f"  Vendor: {data['vendor']}")
        print(f"  Category: {data['predicted_category']}")
        print(f"  Confidence: {data['confidence']:.3f}")
        print(f"  Top 3 probabilities:")
        for cat, prob in list(data['all_probabilities'].items())[:3]:
            print(f"    {cat}: {prob:.3f}")
        return True
    else:
        print(f"[FAIL] API categorization failed: {response.text}")
        return False

def test_ml_model_info():
    """Test ML model info endpoint"""
    print("\nTesting ML model info...")
    
    response = requests.get(f"{BASE_URL}/v1/ml-info")
    
    if response.status_code == 200:
        info = response.json()
        print(f"[OK] Model info retrieved:")
        print(f"  Status: {info['status']}")
        print(f"  Categories: {len(info['categories'])} categories")
        print(f"  Model type: {info['model_type']}")
        return True
    else:
        print(f"[FAIL] Failed to get model info: {response.text}")
        return False

def test_enhanced_sms_parsing():
    """Test SMS parsing with ML categorization"""
    print("\nTesting enhanced SMS parsing with ML...")
    
    test_sms_samples = [
        "Rs 450.00 debited from A/c **1234 on 10-Sep-24 at SWIGGY BANGALORE for UPI/123456789",
        "Thank you for using HDFC Bank NetBanking. You have spent Rs 1,250.50 at AMAZON PAY INDIA on 10-SEP-24",
        "ICICI Bank: Transaction of Rs 75.00 at UBER TRIP on 10-Sep-24 using Card ending 1234",
        "Paid Rs 299.00 to NETFLIX INDIA via Google Pay. UPI transaction ID: 123456789012345",
        "Amount Rs 150.00 paid to APOLLO PHARMACY via PhonePe UPI on 10-Sep-24"
    ]
    
    successful_parses = 0
    
    for i, sms in enumerate(test_sms_samples, 1):
        print(f"  Testing SMS {i}...")
        response = requests.post(
            f"{BASE_URL}/v1/parse-sms",
            json={"sms_text": sms}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    [OK] {data['vendor']:<25} -> {data['category']:<15} (Rs.{data['amount']})")
            successful_parses += 1
        else:
            print(f"    [FAIL] Failed to parse SMS")
    
    print(f"[OK] Successfully parsed {successful_parses}/{len(test_sms_samples)} SMS with ML categorization")
    return successful_parses > 0

def test_category_accuracy():
    """Test categorization accuracy on known samples"""
    print("\nTesting categorization accuracy...")
    
    test_cases = [
        ("SWIGGY BANGALORE", "Food & Dining"),
        ("AMAZON PAY INDIA", "Shopping"),
        ("UBER TRIP", "Transportation"),
        ("NETFLIX INDIA", "Entertainment"),
        ("APOLLO PHARMACY", "Healthcare"),
        ("BYJUS CLASSES", "Education"),
        ("ELECTRICITY BILL", "Utilities"),
        ("HP PETROL PUMP", "Fuel")
    ]
    
    correct_predictions = 0
    
    for vendor, expected_category in test_cases:
        predicted_category, confidence = ml_categorizer.predict_category(vendor)
        
        is_correct = predicted_category == expected_category
        if is_correct:
            correct_predictions += 1
        
        status = "[OK]" if is_correct else "[FAIL]"
        print(f"  {status} {vendor:<20} -> {predicted_category:<15} (expected: {expected_category})")
    
    accuracy = correct_predictions / len(test_cases)
    print(f"\nML Categorization Accuracy: {accuracy:.1%} ({correct_predictions}/{len(test_cases)})")
    
    return accuracy > 0.6  # 60% threshold

def run_ml_categorization_tests():
    """Run comprehensive ML categorization tests"""
    print("=" * 70)
    print("AI Financial Co-Pilot - ML Categorization Test Suite")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Direct ML categorizer
    if test_ml_categorizer_direct():
        tests_passed += 1
    
    # Test 2: ML API endpoint
    if test_ml_api_endpoint():
        tests_passed += 1
    
    # Test 3: ML model info
    if test_ml_model_info():
        tests_passed += 1
    
    # Test 4: Enhanced SMS parsing
    if test_enhanced_sms_parsing():
        tests_passed += 1
    
    # Test 5: Category accuracy
    if test_category_accuracy():
        tests_passed += 1
    
    print("\n" + "=" * 70)
    print(f"ML Test Results: {tests_passed}/{total_tests} tests passed")
    print("=" * 70)
    
    if tests_passed == total_tests:
        print("All ML categorization tests passed!")
        print("Machine Learning integration is working perfectly!")
    else:
        print("Some ML tests failed. Check the output above for details.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    run_ml_categorization_tests()
