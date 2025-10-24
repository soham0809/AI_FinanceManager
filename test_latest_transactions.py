#!/usr/bin/env python3
"""
Test Latest Transactions
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_latest_transactions():
    """Test latest transactions for user"""
    
    print("📋 Testing Latest Transactions")
    print("=" * 40)
    
    # Login
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data['access_token']
        user_id = token_data['user']['id']
        print(f"✅ Logged in as User ID: {user_id}")
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get latest 10 transactions
        print("\n📋 Latest 10 transactions:")
        trans_response = requests.get(f"{BASE_URL}/v1/transactions?limit=10", headers=headers)
        
        if trans_response.status_code == 200:
            transactions = trans_response.json()
            print(f"Found {len(transactions)} transactions")
            
            for i, t in enumerate(transactions):
                print(f"  {i+1}. ID:{t['id']} | {t['vendor']} | ₹{t['amount']} | {t['date']}")
            
            # Check if any TEST SCAN transactions exist
            test_scan_trans = [t for t in transactions if 'TEST SCAN' in str(t.get('vendor', ''))]
            if test_scan_trans:
                print(f"\n✅ Found {len(test_scan_trans)} TEST SCAN transactions in latest 10")
                for t in test_scan_trans:
                    print(f"   ID:{t['id']} | {t['vendor']} | ₹{t['amount']}")
            else:
                print("\n⚠️ No TEST SCAN transactions in latest 10")
                
                # Check all transactions for TEST SCAN
                print("\n🔍 Searching all transactions for TEST SCAN...")
                all_trans_response = requests.get(f"{BASE_URL}/v1/transactions?limit=1000", headers=headers)
                if all_trans_response.status_code == 200:
                    all_transactions = all_trans_response.json()
                    all_test_scan = [t for t in all_transactions if 'TEST SCAN' in str(t.get('vendor', ''))]
                    if all_test_scan:
                        print(f"✅ Found {len(all_test_scan)} TEST SCAN transactions in all {len(all_transactions)} transactions")
                        for t in all_test_scan:
                            print(f"   ID:{t['id']} | {t['vendor']} | ₹{t['amount']} | {t['date']}")
                    else:
                        print("❌ No TEST SCAN transactions found at all")
        else:
            print(f"❌ Failed to get transactions: {trans_response.status_code}")
            print(f"Response: {trans_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    test_latest_transactions()
