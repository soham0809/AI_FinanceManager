import requests
import json
import traceback

def test_sms_parsing():
    """Test SMS parsing with detailed error logging"""
    base_url = "http://172.20.10.3:8000"
    
    # Test SMS message
    test_sms = "You have spent Rs. 250 at SWIGGY on 15-Oct-2025. UPI Ref: 123456789"
    
    print("🔍 Testing SMS parsing endpoint...")
    print(f"📱 Test SMS: {test_sms}")
    
    try:
        response = requests.post(
            f"{base_url}/v1/parse-sms-public",
            json={"sms_text": test_sms},
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SMS Parsing Success: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ SMS Parsing Failed: {response.status_code}")
            print(f"📄 Response Text: {response.text}")
            
            try:
                error_json = response.json()
                print(f"📄 Error JSON: {json.dumps(error_json, indent=2)}")
            except:
                print("📄 Response is not valid JSON")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out - AI processing may be taking too long")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - backend may not be running")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_parsing()
