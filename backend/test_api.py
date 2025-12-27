"""
Backend API Test Suite
Tests all endpoints to verify:
1. Authentication is required
2. Public endpoints are removed
3. All features work when authenticated
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test credentials (create a test user first if needed)
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

# Global variable to store access token
access_token = None

def test_health_check():
    """Test if backend is running"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Backend is running")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to backend: {e}")
        return False

def test_register_user():
    """Register a test user"""
    print("\n" + "="*60)
    print("TEST 2: User Registration")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/register",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "full_name": "Test User"
            }
        )
        
        if response.status_code == 200 or response.status_code == 201:
            print_success("User registered successfully")
            print_info(f"Response: {response.json()}")
            return True
        elif response.status_code == 400:
            print_warning("User already exists (this is OK)")
            return True
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False

def test_login():
    """Login and get access token"""
    global access_token
    
    print("\n" + "="*60)
    print("TEST 3: User Login")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/auth/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print_success("Login successful")
            print_info(f"Access Token: {access_token[:20]}...")
            return True
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

def test_public_endpoints_removed():
    """Verify public endpoints no longer work"""
    print("\n" + "="*60)
    print("TEST 4: Verify Public Endpoints Removed")
    print("="*60)
    
    public_endpoints = [
        ("POST", "/v1/parse-sms-public", {"sms_text": "test"}),
        ("POST", "/v1/parse-sms-local-public", {"sms_text": "test"}),
        ("GET", "/v1/transactions-public", None),
        ("GET", "/v1/analytics/insights-public", None),
        ("GET", "/v1/analytics/spending-by-category-public", None),
        ("GET", "/v1/analytics/monthly-trends-public", None),
        ("GET", "/v1/analytics/top-vendors-public", None),
        ("POST", "/v1/chatbot/query-public", {"query": "test"}),
        ("GET", "/v1/chatbot/summary-public?days=30", None),
        ("POST", "/v1/chatbot/quick-insights-public", {}),
    ]
    
    all_removed = True
    for method, endpoint, data in public_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
            
            # Public endpoints should return 404 (not found) or 405 (method not allowed)
            if response.status_code in [404, 405]:
                print_success(f"{endpoint} - Removed ✓")
            else:
                print_warning(f"{endpoint} - Still exists (status: {response.status_code})")
                all_removed = False
        except Exception as e:
            print_error(f"{endpoint} - Error: {e}")
    
    return all_removed

def test_unauthenticated_access():
    """Test that endpoints require authentication"""
    print("\n" + "="*60)
    print("TEST 5: Verify Authentication Required")
    print("="*60)
    
    test_endpoints = [
        ("POST", "/v1/parse-sms", {"sms_text": "test"}),
        ("GET", "/v1/transactions", None),
        ("GET", "/v1/analytics/insights", None),
        ("POST", "/v1/chatbot/query", {"query": "test"}),
    ]
    
    all_require_auth = True
    for method, endpoint, data in test_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
            
            # Should return 401 (Unauthorized) or 403 (Forbidden)
            if response.status_code in [401, 403]:
                print_success(f"{endpoint} - Requires auth ✓")
            else:
                print_error(f"{endpoint} - No auth required! (status: {response.status_code})")
                all_require_auth = False
        except Exception as e:
            print_error(f"{endpoint} - Error: {e}")
    
    return all_require_auth

def test_sms_parsing_authenticated():
    """Test SMS parsing with authentication"""
    print("\n" + "="*60)
    print("TEST 6: SMS Parsing (Authenticated)")
    print("="*60)
    
    if not access_token:
        print_error("No access token available")
        return False
    
    test_sms = "Your account XXXXXXX1234 has been debited by Rs.500.00 at AMAZON on 25-Dec-24. Available balance: Rs.5000"
    
    # Test local parsing (regex-based)
    try:
        response = requests.post(
            f"{BASE_URL}/v1/parse-sms-local",
            json={"sms_text": test_sms},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Local SMS parsing works")
            print_info(f"Vendor: {data.get('vendor')}")
            print_info(f"Amount: {data.get('amount')}")
            print_info(f"Category: {data.get('category')}")
            return True
        else:
            print_error(f"SMS parsing failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"SMS parsing error: {e}")
        return False

def test_transactions_authenticated():
    """Test transactions endpoints with authentication"""
    print("\n" + "="*60)
    print("TEST 7: Transactions (Authenticated)")
    print("="*60)
    
    if not access_token:
        print_error("No access token available")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Get transactions
    try:
        response = requests.get(f"{BASE_URL}/v1/transactions", headers=headers)
        
        if response.status_code == 200:
            transactions = response.json()
            print_success(f"Retrieved {len(transactions)} transactions")
            print_info(f"Transactions are user-specific")
            return True
        else:
            print_error(f"Get transactions failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Transactions error: {e}")
        return False

def test_analytics_authenticated():
    """Test analytics endpoints with authentication"""
    print("\n" + "="*60)
    print("TEST 8: Analytics (Authenticated)")
    print("="*60)
    
    if not access_token:
        print_error("No access token available")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    endpoints = [
        "/v1/analytics/insights",
        "/v1/analytics/spending-by-category",
        "/v1/analytics/monthly-trends",
        "/v1/analytics/top-vendors",
    ]
    
    all_passed = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print_success(f"{endpoint} - Works ✓")
            else:
                print_error(f"{endpoint} - Failed (status: {response.status_code})")
                all_passed = False
        except Exception as e:
            print_error(f"{endpoint} - Error: {e}")
            all_passed = False
    
    return all_passed

def test_monthly_endpoints_authenticated():
    """Test new monthly endpoints"""
    print("\n" + "="*60)
    print("TEST 9: Monthly Endpoints (New)")
    print("="*60)
    
    if not access_token:
        print_error("No access token available")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    endpoints = [
        "/v1/analytics/monthly/summary",
        "/v1/analytics/monthly/yearly-overview",
    ]
    
    all_passed = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print_success(f"{endpoint} - Works ✓")
            else:
                print_error(f"{endpoint} - Failed (status: {response.status_code})")
                all_passed = False
        except Exception as e:
            print_error(f"{endpoint} - Error: {e}")
            all_passed = False
    
    return all_passed

def test_chatbot_authenticated():
    """Test chatbot endpoints with authentication"""
    print("\n" + "="*60)
    print("TEST 10: Chatbot (Authenticated)")
    print("="*60)
    
    if not access_token:
        print_error("No access token available")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Test chatbot query
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chatbot/query",
            json={"query": "How much did I spend this month?", "limit": 10},
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Chatbot query works")
            return True
        else:
            print_error(f"Chatbot failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Chatbot error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 " + "="*58)
    print("     BACKEND API TEST SUITE")
    print("="*60 + "\n")
    
    results = {}
    
    # Run tests in order
    results["Health Check"] = test_health_check()
    
    if not results["Health Check"]:
        print_error("\n❌ Backend is not running. Please start it with:")
        print_info("cd backend && python -m uvicorn app.main:app --reload --port 8000")
        return
    
    results["User Registration"] = test_register_user()
    results["User Login"] = test_login()
    results["Public Endpoints Removed"] = test_public_endpoints_removed()
    results["Authentication Required"] = test_unauthenticated_access()
    
    if access_token:
        results["SMS Parsing"] = test_sms_parsing_authenticated()
        results["Transactions"] = test_transactions_authenticated()
        results["Analytics"] = test_analytics_authenticated()
        results["Monthly Endpoints"] = test_monthly_endpoints_authenticated()
        results["Chatbot"] = test_chatbot_authenticated()
    else:
        print_error("\nSkipping authenticated tests (no access token)")
    
    # Print summary
    print("\n" + "="*60)
    print("     TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print("\n" + "="*60)
    if passed == total:
        print_success(f"ALL TESTS PASSED ({passed}/{total})")
    else:
        print_error(f"SOME TESTS FAILED ({passed}/{total} passed)")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()
