#!/usr/bin/env python3
"""
Test Authenticated Transactions
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_authenticated_transactions():
    """Test authenticated transaction endpoints"""
    
    print("🔐 Testing Authenticated Transaction Endpoints")
    print("=" * 50)
    
    # Login as testuser
    print("1. Logging in as testuser...")
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data['access_token']
        user_id = token_data['user']['id']
        print(f"   ✅ Login successful - User ID: {user_id}")
        
        # Test authenticated transactions endpoint
        print("\n2. Testing authenticated transactions...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            trans_response = requests.get(f"{BASE_URL}/v1/transactions", headers=headers)
            print(f"   Status: {trans_response.status_code}")
            
            if trans_response.status_code == 200:
                transactions = trans_response.json()
                print(f"   ✅ Success: Found {len(transactions)} transactions for user {user_id}")
                
                if transactions:
                    latest = transactions[0]
                    print(f"   Latest: {latest.get('vendor')} - ₹{latest.get('amount')} - {latest.get('date')}")
                
            else:
                print(f"   ❌ Error: {trans_response.status_code}")
                print(f"   Response: {trans_response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test SMS parsing with authentication
        print("\n3. Testing authenticated SMS parsing...")
        sms_data = {"sms_text": "Spent Rs 99.00 at TEST SCAN on 21-10-2025 using UPI"}
        
        try:
            sms_response = requests.post(f"{BASE_URL}/v1/parse-sms", 
                                       json=sms_data, headers=headers)
            print(f"   Status: {sms_response.status_code}")
            
            if sms_response.status_code == 200:
                result = sms_response.json()
                print(f"   ✅ SMS parsed successfully")
                print(f"   Transaction ID: {result.get('id')}")
                print(f"   Vendor: {result.get('vendor')}")
                print(f"   Amount: ₹{result.get('amount')}")
                
                # Check transactions again to see if it appears
                print("\n4. Checking transactions after SMS parsing...")
                trans_response2 = requests.get(f"{BASE_URL}/v1/transactions", headers=headers)
                if trans_response2.status_code == 200:
                    transactions2 = trans_response2.json()
                    print(f"   ✅ Now has {len(transactions2)} transactions")
                    
                    # Find the new transaction
                    new_trans = [t for t in transactions2 if t.get('vendor') == 'TEST SCAN']
                    if new_trans:
                        print(f"   ✅ Found new transaction: {new_trans[0]}")
                    else:
                        print("   ⚠️ New transaction not found in user's list")
                else:
                    print(f"   ❌ Failed to get updated transactions: {trans_response2.status_code}")
                
            else:
                print(f"   ❌ SMS parsing failed: {sms_response.status_code}")
                print(f"   Response: {sms_response.text}")
                
        except Exception as e:
            print(f"   ❌ SMS parsing exception: {e}")
    
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")

if __name__ == "__main__":
    test_authenticated_transactions()
