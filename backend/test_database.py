"""
Test script for database functionality and API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✓ Health check passed")
        return True
    else:
        print("✗ Health check failed")
        return False

def test_sms_parsing_and_storage():
    """Test SMS parsing with database storage"""
    print("\nTesting SMS parsing and database storage...")
    
    test_sms = "Rs 450.00 debited from A/c **1234 on 10-Sep-24 at SWIGGY BANGALORE for UPI/123456789. Avl Bal Rs 15,234.56"
    
    response = requests.post(
        f"{BASE_URL}/v1/parse-sms",
        json={"sms_text": test_sms},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SMS parsed successfully: {data['vendor']} - ₹{data['amount']}")
        return data
    else:
        print(f"✗ SMS parsing failed: {response.text}")
        return None

def test_get_transactions():
    """Test retrieving transactions from database"""
    print("\nTesting transaction retrieval...")
    
    response = requests.get(f"{BASE_URL}/v1/transactions")
    
    if response.status_code == 200:
        transactions = response.json()
        print(f"✓ Retrieved {len(transactions)} transactions from database")
        return transactions
    else:
        print(f"✗ Failed to retrieve transactions: {response.text}")
        return []

def test_transaction_stats():
    """Test transaction statistics endpoint"""
    print("\nTesting transaction statistics...")
    
    response = requests.get(f"{BASE_URL}/v1/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Statistics retrieved:")
        print(f"  Total transactions: {stats['total_transactions']}")
        print(f"  Total spent: ₹{stats['total_spent']:.2f}")
        print(f"  Total received: ₹{stats['total_received']:.2f}")
        print(f"  Net balance: ₹{stats['net_balance']:.2f}")
        return stats
    else:
        print(f"✗ Failed to retrieve stats: {response.text}")
        return None

def test_categories():
    """Test categories endpoint"""
    print("\nTesting categories...")
    
    response = requests.get(f"{BASE_URL}/v1/categories")
    
    if response.status_code == 200:
        categories = response.json()
        print(f"✓ Retrieved {len(categories)} categories:")
        for cat in categories[:5]:  # Show first 5
            print(f"  - {cat['name']} ({cat['color']})")
        return categories
    else:
        print(f"✗ Failed to retrieve categories: {response.text}")
        return []

def test_search():
    """Test search functionality"""
    print("\nTesting search functionality...")
    
    response = requests.get(f"{BASE_URL}/v1/search?q=swiggy")
    
    if response.status_code == 200:
        results = response.json()
        print(f"✓ Search returned {len(results)} results for 'swiggy'")
        return results
    else:
        print(f"✗ Search failed: {response.text}")
        return []

def test_multiple_sms_samples():
    """Test parsing multiple SMS samples"""
    print("\nTesting multiple SMS samples...")
    
    samples = [
        "Thank you for using HDFC Bank NetBanking. You have spent Rs 1,250.50 at AMAZON PAY INDIA on 10-SEP-24. Available balance: Rs 8,765.43",
        "ICICI Bank: Transaction of Rs 75.00 at UBER TRIP on 10-Sep-24 using Card ending 1234. Current Balance: Rs 12,890.25",
        "You have received Rs 2,000.00 from JOHN DOE via UPI on 10-Sep-24. UPI Ref: 456789123. Available Balance: Rs 14,890.25",
        "Paid Rs 299.00 to NETFLIX INDIA via Google Pay. UPI transaction ID: 123456789012345. Balance: Rs 5,432.10"
    ]
    
    successful_parses = 0
    
    for i, sms in enumerate(samples, 1):
        print(f"  Testing sample {i}...")
        response = requests.post(
            f"{BASE_URL}/v1/parse-sms",
            json={"sms_text": sms},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ {data['vendor']} - ₹{data['amount']} ({data['category'] or 'No category'})")
            successful_parses += 1
        else:
            print(f"    ✗ Failed to parse")
    
    print(f"✓ Successfully parsed {successful_parses}/{len(samples)} SMS samples")
    return successful_parses

def run_comprehensive_test():
    """Run all database tests"""
    print("=" * 60)
    print("AI Financial Co-Pilot Database Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: SMS parsing and storage
    if test_sms_parsing_and_storage():
        tests_passed += 1
    
    # Test 3: Multiple SMS samples
    if test_multiple_sms_samples() > 0:
        tests_passed += 1
    
    # Test 4: Transaction retrieval
    if test_get_transactions():
        tests_passed += 1
    
    # Test 5: Statistics
    if test_transaction_stats():
        tests_passed += 1
    
    # Test 6: Categories
    if test_categories():
        tests_passed += 1
    
    # Bonus: Search test
    test_search()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    print("=" * 60)
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Database integration is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    run_comprehensive_test()
