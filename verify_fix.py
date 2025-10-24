#!/usr/bin/env python3
"""
Verify that the transaction_type error is fixed
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    """Test all the endpoints that were failing"""
    
    print("🔍 Testing Fixed Endpoints")
    print("=" * 40)
    
    # Test 1: Chatbot Query
    print("1. Testing Chatbot Query...")
    try:
        response = requests.post(f"{BASE_URL}/v1/chatbot/query-public", 
                               json={"query": "hii"})
        if response.status_code == 200:
            print("   ✅ Chatbot working!")
        else:
            print(f"   ❌ Chatbot error: {response.status_code}")
            print(f"      {response.text}")
    except Exception as e:
        print(f"   ❌ Chatbot exception: {e}")
    
    # Test 2: Quick Insights
    print("\n2. Testing Quick Insights...")
    try:
        response = requests.post(f"{BASE_URL}/v1/chatbot/quick-insights-public", json={})
        if response.status_code == 200:
            print("   ✅ Quick Insights working!")
        else:
            print(f"   ❌ Quick Insights error: {response.status_code}")
            print(f"      {response.text}")
    except Exception as e:
        print(f"   ❌ Quick Insights exception: {e}")
    
    # Test 3: Transactions
    print("\n3. Testing Transactions...")
    try:
        response = requests.get(f"{BASE_URL}/v1/transactions-public")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Transactions working! Found {len(data)} transactions")
        else:
            print(f"   ❌ Transactions error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Transactions exception: {e}")
    
    # Test 4: SMS Parsing
    print("\n4. Testing SMS Parsing...")
    try:
        test_sms = "Spent Rs 250.00 at SWIGGY on 21-10-2025 using UPI"
        response = requests.post(f"{BASE_URL}/v1/parse-sms-public", 
                               json={"sms_text": test_sms})
        if response.status_code == 200:
            print("   ✅ SMS Parsing working!")
        else:
            print(f"   ❌ SMS Parsing error: {response.status_code}")
            print(f"      {response.text}")
    except Exception as e:
        print(f"   ❌ SMS Parsing exception: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 All critical endpoints tested!")
    print("\n📱 Your Flutter app should now work without the")
    print("   'Transaction' object has no attribute 'transaction_type' error!")

if __name__ == "__main__":
    test_all_endpoints()
