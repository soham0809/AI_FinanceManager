#!/usr/bin/env python3
"""
Test User Isolation
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_user_isolation():
    """Test that users only see their own transactions"""
    
    print("🔐 Testing User Isolation")
    print("=" * 40)
    
    # Test User 1 (testuser)
    print("1. Testing User 1 (testuser)...")
    login1_data = {"username": "testuser", "password": "testpass123"}
    response1 = requests.post(f"{BASE_URL}/auth/login", data=login1_data)
    
    if response1.status_code == 200:
        token1 = response1.json()['access_token']
        print("   ✅ User 1 logged in successfully")
        
        # Get User 1's transactions
        headers1 = {"Authorization": f"Bearer {token1}"}
        trans_response1 = requests.get(f"{BASE_URL}/v1/transactions", headers=headers1)
        
        if trans_response1.status_code == 200:
            transactions1 = trans_response1.json()
            print(f"   ✅ User 1 has {len(transactions1)} transactions")
        else:
            print(f"   ❌ User 1 transactions error: {trans_response1.status_code}")
            print(f"      {trans_response1.text}")
    else:
        print(f"   ❌ User 1 login failed: {response1.status_code}")
    
    # Create User 2
    print("\n2. Creating User 2 (test2@test.com)...")
    register2_data = {
        "email": "test2@test.com",
        "username": "testuser2", 
        "password": "test2@test.com",
        "full_name": "Test User 2"
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register2_data)
    if register_response.status_code in [201, 400]:  # 400 if user already exists
        print("   ✅ User 2 created/exists")
        
        # Login User 2 (try with email as username)
        login2_data = {"username": "test2@test.com", "password": "test2@test.com"}
        response2 = requests.post(f"{BASE_URL}/auth/login", data=login2_data)
        
        if response2.status_code == 200:
            token2 = response2.json()['access_token']
            user2_id = response2.json()['user']['id']
            print(f"   ✅ User 2 logged in successfully (ID: {user2_id})")
            
            # Get User 2's transactions (should be empty)
            headers2 = {"Authorization": f"Bearer {token2}"}
            trans_response2 = requests.get(f"{BASE_URL}/v1/transactions", headers=headers2)
            
            if trans_response2.status_code == 200:
                transactions2 = trans_response2.json()
                print(f"   ✅ User 2 has {len(transactions2)} transactions")
                
                # Parse SMS for User 2
                print("\n3. Adding transaction for User 2...")
                sms_data = {"sms_text": "Spent Rs 150.00 at ZOMATO on 21-10-2025 using UPI"}
                sms_response = requests.post(f"{BASE_URL}/v1/parse-sms", 
                                           json=sms_data, headers=headers2)
                
                if sms_response.status_code == 200:
                    print("   ✅ SMS parsed for User 2")
                    
                    # Check User 2's transactions again
                    trans_response2_new = requests.get(f"{BASE_URL}/v1/transactions", headers=headers2)
                    if trans_response2_new.status_code == 200:
                        transactions2_new = trans_response2_new.json()
                        print(f"   ✅ User 2 now has {len(transactions2_new)} transactions")
                        
                        # Verify User 1 still has the same number
                        trans_response1_check = requests.get(f"{BASE_URL}/v1/transactions", headers=headers1)
                        if trans_response1_check.status_code == 200:
                            transactions1_check = trans_response1_check.json()
                            print(f"   ✅ User 1 still has {len(transactions1_check)} transactions")
                            
                            if len(transactions1_check) != len(transactions2_new):
                                print("   🎉 ISOLATION WORKING! Users have different transaction counts")
                            else:
                                print("   ⚠️ Isolation might not be working - same transaction counts")
                        else:
                            print(f"   ❌ User 1 check failed: {trans_response1_check.status_code}")
                    else:
                        print(f"   ❌ User 2 new transactions failed: {trans_response2_new.status_code}")
                else:
                    print(f"   ❌ SMS parsing failed: {sms_response.status_code}")
                    print(f"      {sms_response.text}")
            else:
                print(f"   ❌ User 2 transactions error: {trans_response2.status_code}")
                print(f"      {trans_response2.text}")
        else:
            print(f"   ❌ User 2 login failed: {response2.status_code}")
    else:
        print(f"   ❌ User 2 registration failed: {register_response.status_code}")

if __name__ == "__main__":
    test_user_isolation()
