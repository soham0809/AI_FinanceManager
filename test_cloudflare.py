#!/usr/bin/env python3
"""
Test Cloudflare Connection
"""
import requests
import json

def test_cloudflare():
    """Test Cloudflare tunnel connection"""
    
    print("🌐 Testing Cloudflare Tunnel Connection")
    print("=" * 50)
    
    # Test Cloudflare URL
    cloudflare_url = "https://ai-finance.sohamm.xyz"
    
    print(f"🔍 Testing: {cloudflare_url}/health")
    
    try:
        response = requests.get(f"{cloudflare_url}/health", timeout=10)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data}")
            print("🎉 CLOUDFLARE TUNNEL IS WORKING!")
            
            # Test SMS parsing through Cloudflare
            print(f"\n🔍 Testing SMS parsing through Cloudflare...")
            sms_data = {"sms_text": "Spent Rs 100.00 at TEST MERCHANT on 21-10-2025 using UPI"}
            
            sms_response = requests.post(f"{cloudflare_url}/v1/parse-sms-public", 
                                       json=sms_data, timeout=30)
            
            if sms_response.status_code == 200:
                print("✅ SMS parsing works through Cloudflare!")
                sms_result = sms_response.json()
                print(f"   Vendor: {sms_result.get('vendor')}")
                print(f"   Amount: {sms_result.get('amount')}")
                print(f"   Category: {sms_result.get('category')}")
            else:
                print(f"❌ SMS parsing failed: {sms_response.status_code}")
                print(f"   Error: {sms_response.text}")
            
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - Cloudflare tunnel might be down")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Also test local connection for comparison
    print(f"\n🏠 Testing Local Connection for comparison...")
    local_url = "http://localhost:8000"
    
    try:
        local_response = requests.get(f"{local_url}/health", timeout=5)
        print(f"✅ Local Status: {local_response.status_code}")
        if local_response.status_code == 200:
            print("✅ Local backend is running")
        else:
            print("❌ Local backend has issues")
    except Exception as e:
        print(f"❌ Local backend error: {e}")

if __name__ == "__main__":
    test_cloudflare()
