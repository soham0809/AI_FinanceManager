import requests
import json

def test_backend():
    base_url = "http://172.20.10.3:8000"
    
    print(f"🔍 Testing backend at {base_url}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        
        # Test transactions endpoint
        response = requests.get(f"{base_url}/v1/transactions-public", timeout=5)
        print(f"✅ Transactions: {response.status_code} - Found {len(response.json())} transactions")
        
        # Test SMS parsing endpoint
        test_sms = "You have spent Rs. 250 at SWIGGY on 15-Oct-2025. UPI Ref: 123456789"
        response = requests.post(
            f"{base_url}/v1/parse-sms-public",
            json={"sms_text": test_sms},
            timeout=10
        )
        print(f"✅ SMS Parsing: {response.status_code} - {response.json()}")
        
        print("🎉 All backend endpoints are working!")
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")

if __name__ == "__main__":
    test_backend()
