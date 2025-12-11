#!/usr/bin/env python3
"""
Test Chatbot Functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_chatbot():
    """Test chatbot query"""
    try:
        query_data = {
            "query": "What are my top spending categories?"
        }
        
        response = requests.post(f"{BASE_URL}/v1/chatbot/query-public", json=query_data)
        print(f"✅ Chatbot Query: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result['response'][:100]}...")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chatbot Query Failed: {e}")
        return False

def test_quick_insights():
    """Test quick insights"""
    try:
        response = requests.post(f"{BASE_URL}/v1/chatbot/quick-insights-public", json={})
        print(f"✅ Quick Insights: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Insights: {result['insights'][:2] if 'insights' in result else result}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Quick Insights Failed: {e}")
        return False

def test_analytics():
    """Test analytics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/v1/analytics/summary-public")
        print(f"✅ Analytics Summary: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Total Spending: ₹{result.get('total_spending', 0):.2f}")
            print(f"   Total Transactions: {result.get('total_transactions', 0)}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analytics Failed: {e}")
        return False

def main():
    print("🤖 Testing AI Finance Manager Chatbot & Analytics")
    print("=" * 60)
    
    # Test Analytics first
    print("📊 Testing Analytics...")
    test_analytics()
    
    print()
    
    # Test Quick Insights
    print("💡 Testing Quick Insights...")
    test_quick_insights()
    
    print()
    
    # Test Chatbot
    print("🤖 Testing Chatbot...")
    test_chatbot()
    
    print()
    print("🎉 Tests completed!")

if __name__ == "__main__":
    main()
