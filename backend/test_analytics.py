"""
Test analytics endpoints and create sample data for visualization
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_analytics_endpoints():
    """Test all analytics endpoints"""
    print("Testing Analytics Endpoints...")
    
    # First, let's add some sample transactions for better visualization
    sample_transactions = [
        "Rs 450.00 debited from A/c **1234 on 10-Sep-24 at SWIGGY BANGALORE for UPI/123456789",
        "Thank you for using HDFC Bank NetBanking. You have spent Rs 1,250.50 at AMAZON PAY INDIA on 10-SEP-24",
        "ICICI Bank: Transaction of Rs 75.00 at UBER TRIP on 10-Sep-24 using Card ending 1234",
        "Paid Rs 299.00 to NETFLIX INDIA via Google Pay. UPI transaction ID: 123456789012345",
        "Amount Rs 150.00 paid to APOLLO PHARMACY via PhonePe UPI on 10-Sep-24",
        "Rs 2500.00 debited from A/c **5678 on 11-Sep-24 at BYJUS CLASSES for UPI/987654321",
        "HDFC Bank: You have spent Rs 85.00 at HP PETROL PUMP on 11-Sep-24",
        "Rs 1200.00 debited from A/c **1234 on 11-Sep-24 at FLIPKART SELLER for UPI/555666777",
        "Paid Rs 45.00 to JIO RECHARGE via Paytm UPI on 11-Sep-24",
        "Amount Rs 350.00 paid to DOMINOS PIZZA via GPay on 11-Sep-24"
    ]
    
    print("Adding sample transactions...")
    for sms in sample_transactions:
        try:
            response = requests.post(f"{BASE_URL}/v1/parse-sms", json={"sms_text": sms})
            if response.status_code == 200:
                data = response.json()
                print(f"  Added: {data['vendor']} - Rs.{data['amount']} ({data['category']})")
        except Exception as e:
            print(f"  Failed to add transaction: {e}")
    
    print("\nTesting Analytics Endpoints:")
    
    # Test 1: Spending by Category
    print("\n1. Testing Spending by Category...")
    try:
        response = requests.get(f"{BASE_URL}/v1/analytics/spending-by-category")
        if response.status_code == 200:
            data = response.json()
            print(f"   Categories found: {len(data['categories'])}")
            print(f"   Total spending: Rs.{data['total_spending']:.2f}")
            for category, amount in data['categories']:
                print(f"     {category}: Rs.{amount:.2f}")
        else:
            print(f"   Failed: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Monthly Trends
    print("\n2. Testing Monthly Trends...")
    try:
        response = requests.get(f"{BASE_URL}/v1/analytics/monthly-trends")
        if response.status_code == 200:
            data = response.json()
            print(f"   Monthly data points: {len(data['monthly_trends'])}")
            for month_data in data['monthly_trends']:
                print(f"     {month_data['month_name']} {month_data['year']}: Rs.{month_data['total_spending']:.2f}")
        else:
            print(f"   Failed: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Spending Insights
    print("\n3. Testing Spending Insights...")
    try:
        response = requests.get(f"{BASE_URL}/v1/analytics/insights")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total transactions: {data['total_transactions']}")
            print(f"   Total spending: Rs.{data['total_spending']:.2f}")
            print(f"   Average transaction: Rs.{data['average_transaction']:.2f}")
            print(f"   Most frequent category: {data['most_frequent_category']}")
            print(f"   Highest spending category: {data['highest_spending_category']}")
            print(f"   Recent 7-day spending: Rs.{data['recent_spending_7days']:.2f}")
        else:
            print(f"   Failed: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Top Vendors
    print("\n4. Testing Top Vendors...")
    try:
        response = requests.get(f"{BASE_URL}/v1/analytics/top-vendors?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"   Top vendors found: {len(data['top_vendors'])}")
            for i, vendor in enumerate(data['top_vendors'], 1):
                print(f"     {i}. {vendor['vendor']}: Rs.{vendor['total_spending']:.2f} ({vendor['transaction_count']} transactions)")
        else:
            print(f"   Failed: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\nAnalytics endpoints test completed!")

if __name__ == "__main__":
    test_analytics_endpoints()
