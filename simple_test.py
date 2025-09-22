#!/usr/bin/env python3
"""
Simple test script to verify backend-frontend connection and analytics flow
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if backend is healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"[PASS] Health Check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"[FAIL] Health Check Failed: {e}")
        return False

def test_sms_parsing():
    """Test SMS parsing functionality"""
    test_sms = "HDFC Bank: Rs.750.00 debited from A/c **1234 on 23-09-24 at SWIGGY INDIA. Avl Bal: Rs.4250.00"
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/parse-sms",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'sms_text': test_sms})
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] SMS Parsing: Success - {result['vendor']} Rs.{result['amount']}")
            return True
        else:
            print(f"[FAIL] SMS Parsing Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] SMS Parsing Error: {e}")
        return False

def test_analytics_endpoints():
    """Test all analytics endpoints"""
    endpoints = [
        "/v1/transactions",
        "/v1/analytics/spending-by-category", 
        "/v1/analytics/monthly-trends",
        "/v1/analytics/insights",
        "/v1/analytics/top-vendors"
    ]
    
    all_passed = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"[PASS] {endpoint}: Success")
                
                # Show sample data for key endpoints
                if endpoint == "/v1/transactions":
                    print(f"   Total transactions: {len(data)}")
                elif endpoint == "/v1/analytics/spending-by-category":
                    if data.get('success'):
                        print(f"   Categories: {len(data.get('categories', []))}")
                        print(f"   Total spending: Rs.{data.get('total_spending', 0):.2f}")
                
            else:
                print(f"[FAIL] {endpoint}: Failed - {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"[FAIL] {endpoint}: Error - {e}")
            all_passed = False
    
    return all_passed

def test_analytics_update_flow():
    """Test that analytics update when new transactions are added"""
    print("\n[INFO] Testing Analytics Update Flow...")
    
    # Get initial analytics
    try:
        initial_response = requests.get(f"{BASE_URL}/v1/analytics/spending-by-category")
        initial_data = initial_response.json()
        initial_spending = initial_data.get('total_spending', 0)
        print(f"   Initial total spending: Rs.{initial_spending:.2f}")
        
        # Add a new transaction via SMS parsing
        test_sms = f"HDFC Bank: Rs.299.00 debited from A/c **1234 on 23-09-24 at NETFLIX INDIA. Avl Bal: Rs.3951.00"
        
        parse_response = requests.post(
            f"{BASE_URL}/v1/parse-sms",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'sms_text': test_sms})
        )
        
        if parse_response.status_code == 200:
            print(f"   [PASS] Added new transaction: Netflix Rs.299")
            
            # Wait a moment for processing
            time.sleep(1)
            
            # Check updated analytics
            updated_response = requests.get(f"{BASE_URL}/v1/analytics/spending-by-category")
            updated_data = updated_response.json()
            updated_spending = updated_data.get('total_spending', 0)
            
            print(f"   Updated total spending: Rs.{updated_spending:.2f}")
            
            if updated_spending > initial_spending:
                print(f"   [PASS] Analytics updated correctly! Increase: Rs.{updated_spending - initial_spending:.2f}")
                return True
            else:
                print(f"   [FAIL] Analytics not updated properly")
                return False
        else:
            print(f"   [FAIL] Failed to add transaction: {parse_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Analytics update test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Backend-Frontend Connection and Analytics Flow\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("SMS Parsing", test_sms_parsing),
        ("Analytics Endpoints", test_analytics_endpoints),
        ("Analytics Update Flow", test_analytics_update_flow)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[INFO] Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("ALL TESTS PASSED! Backend-Frontend connection is working properly.")
        print("Mobile app should now be able to connect and analytics should update.")
    else:
        print("Some tests failed. Please check the issues above.")
    print("="*50)

if __name__ == "__main__":
    main()
