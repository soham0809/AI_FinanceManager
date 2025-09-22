"""
Simple test to debug analytics endpoints
"""

import requests

BASE_URL = "http://localhost:8000"

def test_individual_endpoints():
    """Test each endpoint individually"""
    
    # Test monthly trends
    print("Testing monthly trends endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/v1/analytics/monthly-trends")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test insights
    print("Testing insights endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/v1/analytics/insights")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_individual_endpoints()
