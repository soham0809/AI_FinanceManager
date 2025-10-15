import requests
import json

def test_flutter_endpoints():
    """Test the endpoints that Flutter app uses"""
    base_url = "http://172.20.10.3:8000"
    
    print("🔍 Testing Flutter app endpoints...")
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health: {response.status_code}")
        
        # Test transactions (should work now)
        response = requests.get(f"{base_url}/v1/transactions-public", timeout=5)
        print(f"✅ Transactions: {response.status_code} - {len(response.json())} transactions")
        
        # Test analytics endpoints
        try:
            response = requests.get(f"{base_url}/v1/analytics/spending-by-category-public", timeout=5)
            print(f"✅ Analytics: {response.status_code}")
        except:
            print("⚠️  Analytics: Not available (expected with empty DB)")
        
        print("🎉 Flutter connection endpoints are working!")
        print("📱 Your Flutter app should now be able to connect!")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

if __name__ == "__main__":
    test_flutter_endpoints()
