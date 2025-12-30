#!/usr/bin/env python3
"""
Test Authentication System
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "full_name": "Test User"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"✅ Registration: {response.status_code}")
        if response.status_code == 201:
            print(f"   User created: {response.json()}")
            return True
        else:
            print(f"   Error: {response.text}")
            return response.status_code == 400  # User might already exist
    except Exception as e:
        print(f"❌ Registration Failed: {e}")
        return False

def test_login():
    """Test user login"""
    try:
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"   Access Token: {token_data['access_token'][:50]}...")
            print(f"   User: {token_data['user']['username']}")
            return token_data['access_token']
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return None

def test_protected_endpoint(access_token):
    """Test protected endpoint with token"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"✅ Protected Endpoint: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"   User Info: {user_info}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected Endpoint Failed: {e}")
        return False

def main():
    print("🔐 Testing AI Finance Manager Authentication System")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health():
        print("❌ Backend is not running. Please start it first.")
        return
    
    print()
    
    # Test 2: Registration
    print("📝 Testing Registration...")
    test_register()
    
    print()
    
    # Test 3: Login
    print("🔑 Testing Login...")
    access_token = test_login()
    
    if access_token:
        print()
        # Test 4: Protected Endpoint
        print("🛡️ Testing Protected Endpoint...")
        test_protected_endpoint(access_token)
    
    print()
    print("🎉 Authentication tests completed!")

if __name__ == "__main__":
    main()
