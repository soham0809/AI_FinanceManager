#!/usr/bin/env python3
"""
Test Flutter App Endpoints via Cloudflare
"""
import requests
import json

def test_flutter_endpoints():
    """Test all endpoints that Flutter app uses via Cloudflare"""
    
    print("📱 Testing Flutter App Endpoints via Cloudflare")
    print("=" * 60)
    
    base_url = "https://ai-finance.sohamm.xyz"
    
    # Test 1: Health Check
    print("1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Health check working")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Public Transactions
    print("\n2. Public Transactions...")
    try:
        response = requests.get(f"{base_url}/v1/transactions-public", timeout=10)
        if response.status_code == 200:
            transactions = response.json()
            print(f"   ✅ Transactions working: {len(transactions)} found")
        else:
            print(f"   ❌ Transactions failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Transactions error: {e}")
    
    # Test 3: SMS Parsing
    print("\n3. SMS Parsing...")
    try:
        sms_data = {"sms_text": "Spent Rs 250.00 at SWIGGY on 21-10-2025 using UPI"}
        response = requests.post(f"{base_url}/v1/parse-sms-public", 
                               json=sms_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ SMS parsing working")
            print(f"      Vendor: {result.get('vendor')}")
            print(f"      Amount: ₹{result.get('amount')}")
            print(f"      Category: {result.get('category')}")
        else:
            print(f"   ❌ SMS parsing failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ SMS parsing error: {e}")
    
    # Test 4: Authentication
    print("\n4. Authentication...")
    try:
        # Try to login with test user
        login_data = {"username": "testuser", "password": "testpass123"}
        response = requests.post(f"{base_url}/auth/login", data=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Authentication working")
            print(f"      User: {token_data['user']['username']}")
            
            # Test authenticated endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            auth_response = requests.get(f"{base_url}/v1/transactions", 
                                       headers=headers, timeout=10)
            if auth_response.status_code == 200:
                auth_transactions = auth_response.json()
                print(f"   ✅ Authenticated transactions: {len(auth_transactions)} found")
            else:
                print(f"   ⚠️ Authenticated transactions: {auth_response.status_code}")
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
    
    # Test 5: Chatbot
    print("\n5. Chatbot...")
    try:
        chatbot_data = {"query": "What are my top spending categories?"}
        response = requests.post(f"{base_url}/v1/chatbot/query-public", 
                               json=chatbot_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Chatbot working")
            print(f"      Response: {result.get('response', '')[:50]}...")
        else:
            print(f"   ❌ Chatbot failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Chatbot error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 CLOUDFLARE TESTING COMPLETE!")
    print("\n📱 Your Flutter app should now work with:")
    print("   useCloudflare = true")
    print("   URL: https://ai-finance.sohamm.xyz")
    print("\n🔧 Next steps:")
    print("   1. Hot reload your Flutter app (press 'r')")
    print("   2. The app will now use Cloudflare instead of local IP")
    print("   3. SMS parsing should work without USB connection!")

if __name__ == "__main__":
    test_flutter_endpoints()
